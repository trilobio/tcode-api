"""Move a Biotix tip box through deck slots 1-16.

In every slot (including the last), a single-channel pipette picks up and returns the
four corner tips; the gripper then moves the box to the next slot. The tip box labware
is selected to match the pipette volume (e.g. a P300 pipette uses the uTIP P300 box).

With --continue-through-failures, a failed tip pickup skips the rest of that slot's
corner check and continues with the box move to the next slot, instead of aborting.
"""

import dataclasses
import pathlib
import time

import plac  # type: ignore [import-untyped]

import tcode_api.api as tc
from tcode_api.cli import (
    DEFAULT_SERVICER_URL,
    output_file_path_annotation,
    robot_serial_number_annotation,
    servicer_url_annotation,
)
from tcode_api.servicer import TCodeServicerClient
from tcode_api.utilities import (
    describe_pipette_tip_box,
    describe_pipette_tip_group,
    generate_id,
    load_labware,
)

DECK_SLOTS = [f"DeckSlot_{i}" for i in range(1, 17)]
CORNER_INDICES = [0, 11, 84, 95]  # Four corners of 8x12 tip box

# Biotix uTIP box sizes available in tcode_labware, keyed by max pipette volume in uL.
SUPPORTED_PIPETTE_VOLUMES = (20, 100, 200, 250, 300, 1000)


def tip_box_labware_name(pipette_volume: float) -> str:
    """Return the Biotix uTIP box labware name matching a pipette's max volume."""
    if pipette_volume not in SUPPORTED_PIPETTE_VOLUMES:
        raise ValueError(
            f"No Biotix uTIP box for a {pipette_volume} uL pipette; "
            f"supported volumes: {', '.join(str(v) for v in SUPPORTED_PIPETTE_VOLUMES)}"
        )
    return f"biotix_utip_p{int(pipette_volume)}_box"


@dataclasses.dataclass
class WalkthroughPlan:
    """TCode command batches for one demo plate walkthrough run.

    ``slot_batches`` holds one ``(slot_name, corner_check_commands, move_box_commands)``
    tuple per deck slot; the move batch is empty for the last slot.
    """

    robot_id: str
    gripper_id: str
    pipette_id: str
    tip_box_id: str
    deck_slots: list[str]
    setup_commands: list[tc.TCode]
    slot_batches: list[tuple[str, list[tc.TCode], list[tc.TCode]]]
    final_commands: list[tc.TCode]

    def full_script(self, name: str, description: str | None) -> tc.TCodeScript:
        """Flatten all batches into a single TCodeScript."""
        script = tc.TCodeScript.new(name=name, description=description)
        script.commands = list(self.setup_commands)
        for _, corner_commands, move_commands in self.slot_batches:
            script.commands.extend(corner_commands)
            script.commands.extend(move_commands)
        script.commands.extend(self.final_commands)
        return script


def build_walkthrough_plan(
    robot_sn: str | None = None, pipette_volume: float = 300
) -> WalkthroughPlan:
    """Build the walkthrough's TCode command batches."""
    # FLEET
    robot_id, gripper_id, pipette_id, tip_box_id = [generate_id() for _ in range(4)]
    # serial_number is matched by the tcode servicer's robot resolver
    # (tcode/resolver/robots.py), pinning the script to that robot.
    robot_descriptor = (
        tc.RobotDescriptor(serial_number=robot_sn) if robot_sn else tc.RobotDescriptor()
    )
    setup_commands: list[tc.TCode] = [
        tc.ADD_ROBOT(id=robot_id, descriptor=robot_descriptor),
        tc.ADD_TOOL(robot_id=robot_id, id=gripper_id, descriptor=tc.GripperDescriptor()),
        tc.ADD_TOOL(
            robot_id=robot_id,
            id=pipette_id,
            descriptor=tc.SingleChannelPipetteDescriptor(
                max_volume=tc.ValueWithUnits(units="ul", magnitude=pipette_volume)
            ),
        ),
    ]

    # LABWARE
    setup_commands.append(
        tc.CREATE_LABWARE(
            robot_id=robot_id,
            description=load_labware(tip_box_labware_name(pipette_volume)),
            holder=tc.LabwareHolderName(
                robot_id=robot_id,
                name=DECK_SLOTS[0],
            ),
        ),
    )
    setup_commands.append(tc.ADD_LABWARE(id=tip_box_id, descriptor=describe_pipette_tip_box()))

    # One tip group per well (8x12)
    tip_group_ids: list[str] = []
    for idx in range(96):
        tip_group_id = generate_id()
        tip_group_ids.append(tip_group_id)
        setup_commands.append(
            tc.ADD_PIPETTE_TIP_GROUP(
                robot_id=robot_id,
                id=tip_group_id,
                descriptor=describe_pipette_tip_group(
                    row_count=1,
                    column_count=1,
                ),
            )
        )

    # ACTIONS
    # Start with pipette to exercise corners before first move
    setup_commands.append(tc.SWAP_TO_TOOL(robot_id=robot_id, id=pipette_id))
    setup_commands.append(tc.COMMENT(text="Walk tip box through all deck slots"))

    # Per slot: a corner-check batch and a move-box batch (empty for the last slot)
    slot_batches: list[tuple[str, list[tc.TCode], list[tc.TCode]]] = []
    for idx, current_slot in enumerate(DECK_SLOTS):
        corner_commands: list[tc.TCode] = [tc.COMMENT(text=f"Corner check in {current_slot}")]
        for labware_index in CORNER_INDICES:
            tip_group_id = tip_group_ids[labware_index]
            corner_commands.append(
                tc.RETRIEVE_PIPETTE_TIP_GROUP(robot_id=robot_id, id=tip_group_id)
            )
            corner_commands.append(tc.RETURN_PIPETTE_TIP_GROUP(robot_id=robot_id))

        move_commands: list[tc.TCode] = []
        if current_slot != DECK_SLOTS[-1]:
            next_slot = DECK_SLOTS[idx + 1]
            move_commands = [
                tc.SWAP_TO_TOOL(robot_id=robot_id, id=gripper_id),
                tc.PICK_UP_LABWARE(
                    robot_id=robot_id,
                    labware_id=tip_box_id,
                    grasp_type=tc.GraspType.LIFT,
                ),
                tc.PUT_DOWN_LABWARE(
                    robot_id=robot_id,
                    holder=tc.LabwareHolderName(
                        robot_id=robot_id,
                        name=next_slot,
                    ),
                ),
                tc.SWAP_TO_TOOL(robot_id=robot_id, id=pipette_id),
            ]

        slot_batches.append((current_slot, corner_commands, move_commands))

    final_commands: list[tc.TCode] = [tc.RETURN_TOOL(robot_id=robot_id)]

    return WalkthroughPlan(
        robot_id=robot_id,
        gripper_id=gripper_id,
        pipette_id=pipette_id,
        tip_box_id=tip_box_id,
        deck_slots=list(DECK_SLOTS),
        setup_commands=setup_commands,
        slot_batches=slot_batches,
        final_commands=final_commands,
    )


def run_commands(client: TCodeServicerClient, commands: list[tc.TCode]) -> str | None:
    """Schedule and execute a batch of commands, blocking until it finishes.

    :returns: None on success, or the failure description if execution failed. On
        failure, the remainder of the batch is cleared from the servicer's schedule.
    """
    for command in commands:
        rsp = client.schedule_command(generate_id(), command)
        if not rsp.result.success:
            raise RuntimeError(
                f"tcode service schedule_command({command.type}) unsuccessful: {rsp.result.message}"
            )

    client.set_run_state(True)
    while True:
        time.sleep(0.1)
        status = client.get_status()

        if not status.result.success:
            client.set_run_state(False)
            # Drop the failed command and the rest of this batch.
            client.clear_schedule()
            details = status.result.details or {}
            return details.get("error", None) or status.result.message or status.result.code

        if status.operation_count == 0:
            client.set_run_state(False)
            return None


def run_walkthrough(client: TCodeServicerClient, plan: WalkthroughPlan) -> list[str]:
    """Run the walkthrough batch-wise, starting from a clean fleet state.

    A tip pickup failure abandons the rest of that slot's corner check and continues
    with the box move to the next slot; any other failure raises. The TCode resolution
    (robot/tool/labware ids in ``plan``) remains active on the servicer afterwards.

    :returns: Names of the slots whose corner check was abandoned.
    """
    # Clean the environment the same way run_script() does.
    client.clear_schedule()
    client.clear_labware()
    client.clear_tcode_resolution()
    client.clear_tf_tree_history()
    client.discover_fleet()

    failure = run_commands(client, plan.setup_commands)
    if failure is not None:
        raise RuntimeError(f"Setup failed: {failure}")

    skipped_slots: list[str] = []
    for slot_name, corner_commands, move_commands in plan.slot_batches:
        failure = run_commands(client, corner_commands)
        if failure is not None:
            if "PipetteTipPickupFailure" not in failure:
                raise RuntimeError(f"Corner check in {slot_name} failed: {failure}")
            skipped_slots.append(slot_name)
            print(f"Tip pickup failed in {slot_name}; skipping to the next slot. ({failure})")

        if move_commands:
            failure = run_commands(client, move_commands)
            if failure is not None:
                raise RuntimeError(f"Moving tip box out of {slot_name} failed: {failure}")

    failure = run_commands(client, plan.final_commands)
    if failure is not None:
        raise RuntimeError(f"Returning tool failed: {failure}")

    return skipped_slots


@plac.annotations(
    servicer_url=servicer_url_annotation,
    output_file_path=output_file_path_annotation,
    robot_sn=robot_serial_number_annotation,
    pipette_volume=plac.Annotation(
        "Max pipette volume in uL; must match an available Biotix uTIP box "
        f"({', '.join(str(v) for v in SUPPORTED_PIPETTE_VOLUMES)})",
        kind="option",
        abbrev="v",
        type=float,
    ),
    continue_through_failures=plac.Annotation(
        "On a tip pickup failure, skip the rest of that slot's corner check and continue "
        "with the next slot instead of aborting.",
        kind="flag",
        abbrev="c",
    ),
)
def main(
    servicer_url: str = DEFAULT_SERVICER_URL,
    output_file_path: pathlib.Path | None = None,
    robot_sn: str | None = None,
    pipette_volume: float = 300,
    continue_through_failures: bool = False,
) -> None:
    plan = build_walkthrough_plan(robot_sn=robot_sn, pipette_volume=pipette_volume)

    if output_file_path is not None:
        script = plan.full_script(name=__file__, description=__doc__)
        with output_file_path.open("w") as f:
            script.write(f)

    client = TCodeServicerClient(servicer_url=servicer_url)

    if not continue_through_failures:
        client.run_script(plan.full_script(name=__file__, description=__doc__))
        return

    skipped_slots = run_walkthrough(client, plan)
    if skipped_slots:
        print("Corner checks abandoned after a tip pickup failure in: " + ", ".join(skipped_slots))
    else:
        print("Walkthrough completed with no tip pickup failures.")


if __name__ == "__main__":
    plac.call(main)
