"""Run the demo plate walkthrough with a deck-slot recalibration feedback loop.

Runs the walkthrough, reads the tip-pickup stats the tcode server wrote, and — if any
deck slot needed pickup retries (or had a pickup failure) — recalibrates only the
affected slots with the probe (via CALIBRATE_LABWARE_HOLDER) and runs the walkthrough
again. Repeats until a run is clean or the recalibration attempt budget is exhausted;
a walkthrough run always follows a recalibration. Results are printed after every run.

Requirements:
- The tcode server must run with the TIP_PICKUP_STATS_FILE environment variable set,
  and this script must be given the same path (it reads the file directly, so run it
  on the same host as the server).
- The probe must have an assigned tool holder slot in the database.
- The tip box must physically start in the first deck slot; between runs, this script
  moves it back there with the gripper.
"""

import json
import pathlib
import re
import sys
from collections import defaultdict

import plac  # type: ignore [import-untyped]
from demo_plate_slot_walkthrough import (
    WalkthroughPlan,
    build_walkthrough_plan,
    run_commands,
    run_walkthrough,
)

import tcode_api.api as tc
from tcode_api.cli import DEFAULT_SERVICER_URL, servicer_url_annotation
from tcode_api.servicer import TCodeServicerClient
from tcode_api.utilities import generate_id


def count_lines(file_path: pathlib.Path) -> int:
    """Number of lines currently in the file (0 if it does not exist)."""
    if not file_path.exists():
        return 0
    return len(file_path.read_text().splitlines())


def read_records_after_line(file_path: pathlib.Path, start_line: int) -> list[dict]:
    """Read the tip-pickup stats records appended after the given line number."""
    if not file_path.exists():
        return []
    records = []
    for line in file_path.read_text().splitlines()[start_line:]:
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"Skipping invalid stats line: {line!r}", file=sys.stderr)
    return records


def deck_slot_sort_key(deck_slot: str) -> tuple[int, str]:
    """Sort deck slots numerically (DeckSlot_2 before DeckSlot_10), unknowns last."""
    match = re.search(r"(\d+)$", deck_slot)
    if match is None:
        return (sys.maxsize, deck_slot)
    return (int(match.group(1)), deck_slot)


def describe_record(record: dict) -> str:
    """One-line description of a pickup that needed retries or failed."""
    retries = record["retries"]
    retry_noun = "retry" if retries == 1 else "retries"
    outcome = "ok" if record["result"] == "ok" else f"FAILED ({record['result']})"
    return f"{record['tip']}: {retries} {retry_noun} -> {outcome}"


def summarize(records: list[dict]) -> str:
    """Compact per-deck-slot summary: "ok" for clean slots, else only the problem tips."""
    records_by_deck_slot: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        records_by_deck_slot[record["deck_slot"]].append(record)

    lines = []
    for deck_slot in sorted(records_by_deck_slot, key=deck_slot_sort_key):
        slot_records = records_by_deck_slot[deck_slot]
        problems = [r for r in slot_records if r["retries"] > 0 or r["result"] != "ok"]
        if not problems:
            lines.append(f"{deck_slot}: ok")
        else:
            lines.append(f"{deck_slot}: " + "; ".join(describe_record(r) for r in problems))
    return "\n".join(lines)


def affected_slots(records: list[dict]) -> list[str]:
    """Deck slots with at least one pickup that needed retries or failed, sorted."""
    slots = {
        record["deck_slot"]
        for record in records
        if record["retries"] > 0 or record["result"] != "ok"
    }
    return sorted(slots, key=deck_slot_sort_key)


def build_recalibration_commands(
    plan: WalkthroughPlan, probe_id: str, slots: list[str]
) -> list[tc.TCode]:
    """Commands to recalibrate the given slots and return the tip box to the first slot.

    After a walkthrough run the box sits in the last deck slot, so that slot (if
    affected) is calibrated only after the box has been moved back to the first slot;
    the first slot (if affected) is calibrated before the box arrives.
    """
    box_slot = plan.deck_slots[-1]
    start_slot = plan.deck_slots[0]

    def calibrate(slot: str) -> tc.TCode:
        return tc.CALIBRATE_LABWARE_HOLDER(
            robot_id=plan.robot_id,
            location=tc.LocationAsLabwareHolder(robot_id=plan.robot_id, labware_holder_name=slot),
        )

    commands: list[tc.TCode] = [
        tc.ADD_TOOL(robot_id=plan.robot_id, id=probe_id, descriptor=tc.ProbeDescriptor())
    ]

    slots_before_box_move = [slot for slot in slots if slot != box_slot]
    if slots_before_box_move:
        commands.append(tc.SWAP_TO_TOOL(robot_id=plan.robot_id, id=probe_id))
        commands.extend(calibrate(slot) for slot in slots_before_box_move)

    commands += [
        tc.SWAP_TO_TOOL(robot_id=plan.robot_id, id=plan.gripper_id),
        tc.PICK_UP_LABWARE(
            robot_id=plan.robot_id,
            labware_id=plan.tip_box_id,
            grasp_type=tc.GraspType.LIFT,
        ),
        tc.PUT_DOWN_LABWARE(
            robot_id=plan.robot_id,
            holder=tc.LabwareHolderName(robot_id=plan.robot_id, name=start_slot),
        ),
    ]

    if box_slot in slots:
        commands.append(tc.SWAP_TO_TOOL(robot_id=plan.robot_id, id=probe_id))
        commands.append(calibrate(box_slot))

    commands.append(tc.RETURN_TOOL(robot_id=plan.robot_id))
    return commands


@plac.annotations(
    stats_file_path=plac.Annotation(
        "Stats JSONL file the tcode server writes (same path as its TIP_PICKUP_STATS_FILE)",
        type=pathlib.Path,
    ),
    servicer_url=servicer_url_annotation,
    robot_sn=plac.Annotation(
        "Robot serial number to target (optional).",
        kind="option",
        abbrev="r",
    ),
    pipette_volume=plac.Annotation(
        "Max pipette volume in uL", kind="option", abbrev="v", type=float
    ),
    recalibration_attempts=plac.Annotation(
        "Maximum number of deck-slot recalibration passes between walkthrough runs.",
        kind="option",
        abbrev="a",
        type=int,
    ),
)
def main(
    stats_file_path: pathlib.Path,
    servicer_url: str = DEFAULT_SERVICER_URL,
    robot_sn: str | None = None,
    pipette_volume: float = 300,
    recalibration_attempts: int = 1,
) -> None:
    if recalibration_attempts < 0:
        raise SystemExit("recalibration-attempts must be >= 0")

    client = TCodeServicerClient(servicer_url=servicer_url)
    plan = build_walkthrough_plan(robot_sn=robot_sn, pipette_volume=pipette_volume)
    total_runs = recalibration_attempts + 1

    for run_index in range(total_runs):
        print(f"=== Walkthrough run {run_index + 1}/{total_runs} ===")
        stats_start_line = count_lines(stats_file_path)
        run_walkthrough(client, plan)

        records = read_records_after_line(stats_file_path, stats_start_line)
        if not records:
            raise RuntimeError(
                f"No new tip pickup stats appeared in {stats_file_path}. "
                "Is TIP_PICKUP_STATS_FILE set to this path on the tcode server?"
            )
        print(summarize(records))

        problem_slots = affected_slots(records)
        recalibratable = [slot for slot in problem_slots if slot in plan.deck_slots]
        unrecalibratable = [slot for slot in problem_slots if slot not in plan.deck_slots]
        if unrecalibratable:
            print(
                "Cannot recalibrate problem locations outside the walkthrough deck slots: "
                + ", ".join(unrecalibratable)
            )

        if not recalibratable:
            print("Clean run; no recalibration needed.")
            return

        if run_index == total_runs - 1:
            print(
                "Recalibration attempt budget exhausted; slots still needing attention: "
                + ", ".join(recalibratable)
            )
            return

        print(f"Recalibrating: {', '.join(recalibratable)}")
        failure = run_commands(
            client, build_recalibration_commands(plan, generate_id(), recalibratable)
        )
        if failure is not None:
            raise RuntimeError(f"Recalibration failed: {failure}")


if __name__ == "__main__":
    plac.call(main)
