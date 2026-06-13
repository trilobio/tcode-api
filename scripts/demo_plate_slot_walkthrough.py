"""Move a Biotix P300 tip box through deck slots 1-16.

For each slot hop, a single-channel pipette picks up and returns the four corner tips
before the gripper moves the box to the next slot.
"""

import pathlib

import plac  # type: ignore [import-untyped]

import tcode_api.api as tc
from tcode_api.cli import (
    DEFAULT_SERVICER_URL,
    output_file_path_annotation,
    servicer_url_annotation,
)
from tcode_api.servicer import TCodeServicerClient
from tcode_api.utilities import (
    describe_pipette_tip_box,
    describe_pipette_tip_group,
    generate_id,
    load_labware,
)


@plac.annotations(
    servicer_url=servicer_url_annotation,
    output_file_path=output_file_path_annotation,
    robot_sn=plac.Annotation(
        "Robot serial number to target (optional).",
        kind="option",
        abbrev="r",
    ),
    pipette_volume=plac.Annotation(
        "Max pipette volume in uL", kind="option", abbrev="v", type=float
    ),
)
def main(
    servicer_url: str = DEFAULT_SERVICER_URL,
    output_file_path: pathlib.Path | None = None,
    robot_sn: str | None = None,
    pipette_volume: float = 300,
) -> None:
    script = tc.TCodeScript.new(
        name=__file__,
        description=__doc__,
    )

    # FLEET
    robot_id, gripper_id, pipette_id, tip_box_id = [generate_id() for _ in range(4)]
    # serial_number is matched by the tcode servicer's robot resolver
    # (tcode/resolver/robots.py), pinning the script to that robot.
    robot_descriptor = (
        tc.RobotDescriptor(serial_number=robot_sn) if robot_sn else tc.RobotDescriptor()
    )
    script.commands.append(tc.ADD_ROBOT(id=robot_id, descriptor=robot_descriptor))
    script.commands.append(
        tc.ADD_TOOL(robot_id=robot_id, id=gripper_id, descriptor=tc.GripperDescriptor())
    )
    script.commands.append(
        tc.ADD_TOOL(
            robot_id=robot_id,
            id=pipette_id,
            descriptor=tc.SingleChannelPipetteDescriptor(
                max_volume=tc.ValueWithUnits(units="ul", magnitude=pipette_volume)
            ),
        )
    )

    # LABWARE
    deck_slots = [f"DeckSlot_{i}" for i in range(1, 17)]
    script.commands.append(
        tc.CREATE_LABWARE(
            robot_id=robot_id,
            description=load_labware("biotix_utip_p300_box"),
            holder=tc.LabwareHolderName(
                robot_id=robot_id,
                name=deck_slots[0],
            ),
        ),
    )
    script.commands.append(tc.ADD_LABWARE(id=tip_box_id, descriptor=describe_pipette_tip_box()))

    # One tip group per well (8x12)
    tip_group_ids: list[str] = []
    for idx in range(96):
        tip_group_id = generate_id()
        tip_group_ids.append(tip_group_id)
        script.commands.append(
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
    corner_indices = [0, 11, 84, 95]  # Four corners of 8x12 tip box

    # Start with pipette to exercise corners before first move
    script.commands.append(tc.SWAP_TO_TOOL(robot_id=robot_id, id=pipette_id))
    script.commands.append(tc.COMMENT(text="Walk tip box through all deck slots"))

    for idx, next_slot in enumerate(deck_slots[1:], start=1):
        current_slot = deck_slots[idx - 1]

        script.commands.append(tc.COMMENT(text=f"Corner check in {current_slot}"))
        for labware_index in corner_indices:
            tip_group_id = tip_group_ids[labware_index]
            script.commands.append(
                tc.RETRIEVE_PIPETTE_TIP_GROUP(robot_id=robot_id, id=tip_group_id)
            )
            script.commands.append(tc.RETURN_PIPETTE_TIP_GROUP(robot_id=robot_id))

        script.commands.append(tc.SWAP_TO_TOOL(robot_id=robot_id, id=gripper_id))
        script.commands.append(
            tc.PICK_UP_LABWARE(
                robot_id=robot_id,
                labware_id=tip_box_id,
                grasp_type=tc.GraspType.LIFT,
            )
        )
        script.commands.append(
            tc.PUT_DOWN_LABWARE(
                robot_id=robot_id,
                holder=tc.LabwareHolderName(
                    robot_id=robot_id,
                    name=next_slot,
                ),
            )
        )

        # Prepare for next corner check unless we're done
        if next_slot != deck_slots[-1]:
            script.commands.append(tc.SWAP_TO_TOOL(robot_id=robot_id, id=pipette_id))

    script.commands.append(tc.RETURN_TOOL(robot_id=robot_id))

    if output_file_path is not None:
        with output_file_path.open("w") as f:
            script.write(f)

    client = TCodeServicerClient(servicer_url=servicer_url)
    client.run_script(script)


if __name__ == "__main__":
    plac.call(main)
