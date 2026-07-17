"""Replay a path taught via teach_path.py.

Mirrors teach_path's setup: picks up a labware first, moves to the first point of
the path with a SAFE move, replays the remaining points as DIRECT moves, then puts
the labware back where it started. Pass --direction reverse to play the path in
reverse.
"""

from __future__ import annotations

import pathlib
from typing import Literal

import plac  # type: ignore [import-untyped]
from teach_path import (
    DEFAULT_DECK_SLOT,
    DEFAULT_FILE_PATH,
    DEFAULT_LABWARE,
    DEFAULT_TCODE_SERVICE_URL,
    Path,
    _generate_pick_up_labware_script,
    deck_slot_name_annotation,
    filepath_annotation,
    gripper_serial_number_annotation,
    labware_name_annotation,
    serial_number_annotation,
    tcode_url_annotation,
    yield_path,
)

import tcode_api.api as tc
from tcode_api.servicer import TCodeServicerClient
from tcode_api.utilities import create_transform


def _direction_to_mode(raw: str) -> Literal["forward", "backward"]:
    """Map a user-facing direction onto yield_path's mode argument."""
    value = raw.lower()
    if value in ("forward", "f", "fwd"):
        return "forward"
    if value in ("reverse", "backward", "back", "r", "b", "rev"):
        return "backward"
    raise ValueError(f"Unrecognized direction {raw!r}; use 'forward' or 'reverse'")


@plac.annotations(
    tcode_service_url=tcode_url_annotation,
    direction=plac.Annotation(
        "Direction to replay the path: forward or reverse",
        abbrev="dir",
        kind="option",
        type=str,
    ),
    deck_slot_name=deck_slot_name_annotation,
    labware_name=labware_name_annotation,
    filepath=filepath_annotation,
    robot_serial_number=serial_number_annotation,
    gripper_serial_number=gripper_serial_number_annotation,
)
def replay(
    tcode_service_url: str = DEFAULT_TCODE_SERVICE_URL,
    direction: str = "forward",
    deck_slot_name: str = DEFAULT_DECK_SLOT,
    labware_name: str = DEFAULT_LABWARE,
    filepath: pathlib.Path = DEFAULT_FILE_PATH,
    robot_serial_number: str | None = None,
    gripper_serial_number: str | None = None,
) -> None:
    """Replay a taught Path forward or in reverse."""
    mode = _direction_to_mode(direction)

    with filepath.open("r") as io_obj:
        path = Path.read(io_obj)
    if not path.points:
        raise ValueError(f"Path in {filepath} has no points to replay.")

    tc_client = TCodeServicerClient(servicer_url=tcode_service_url)

    # Pick up the labware first, exactly as teach_path does.
    pickup_script, robot_id, _, __ = _generate_pick_up_labware_script(
        deck_slot_name,
        labware_name,
        robot_serial_number or "",
        gripper_serial_number=gripper_serial_number,
    )
    tc_client.run_script(pickup_script)

    # Replay the path: SAFE move to the first point, then DIRECT moves through the rest.
    replay_script = tc.TCodeScript.new(
        name=__file__,
        description=f"Replay loaded Path ({mode}).",
    )
    for index, matrix in enumerate(yield_path(path, mode)):
        replay_script.commands.append(
            tc.MOVE_TO_LOCATION(
                robot_id=robot_id,
                location=tc.LocationRelativeToRobot(robot_id=robot_id, matrix=matrix),
                path_type=tc.PathType.SAFE if index == 0 else tc.PathType.DIRECT,
            )
        )

    # Put the labware back in the deck slot it was picked up from.
    replay_script.commands.append(
        tc.PUT_DOWN_LABWARE(
            robot_id=robot_id,
            holder=tc.LabwareHolderName(robot_id=robot_id, name=deck_slot_name),
            offset_transform=create_transform(),
        )
    )

    tc_client.run_script(replay_script, clean_environment=False)


if __name__ == "__main__":
    plac.call(replay)
