"""Generate Basic Fluid Movement TCode script for unittesting."""

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
    generate_id,
    load_labware,
    ul,
)


@plac.annotations(
    servicer_url=servicer_url_annotation,
    output_file_path=output_file_path_annotation,
)
def main(
    servicer_url: str = DEFAULT_SERVICER_URL,
    output_file_path: pathlib.Path | None = None,
) -> None:
    pipette_volume = ul(300)
    channel_count = 1
    pipette_descriptor = tc.SingleChannelPipetteDescriptor(max_volume=pipette_volume)

    script_a = tc.TCodeScript.new(
        name=f"Pick up and Eject Tip (C1P{pipette_volume.magnitude}) - Part A",
    )

    (
        robot_id,
        pipette_id,
        tip_box_id,
        pipette_tip_group_id_1,
        pipette_tip_group_id_2,
        trash_can_id,
    ) = [generate_id() for _ in range(6)]

    # Resolve robot and pipette
    script_a.commands.append(tc.ADD_ROBOT(id=robot_id, descriptor=tc.RobotDescriptor()))
    script_a.commands.append(
        tc.ADD_TOOL(
            robot_id=robot_id,
            id=pipette_id,
            descriptor=pipette_descriptor,
        )
    )

    # Create labware
    script_a.commands.append(
        tc.CREATE_LABWARE(
            robot_id=robot_id,
            description=load_labware("biotix_utip_p300_box"),
            holder=tc.LabwareHolderName(robot_id=robot_id, name="DeckSlot_8"),
        )
    )
    script_a.commands.append(
        tc.CREATE_LABWARE(
            robot_id=robot_id,
            description=load_labware("3d_printed_trash_can"),
            holder=tc.LabwareHolderName(robot_id=robot_id, name="DeckSlot_11"),
        )
    )

    # Resolve labware
    script_a.commands.append(
        tc.ADD_LABWARE(id=tip_box_id, descriptor=describe_pipette_tip_box(full=True))
    )
    script_a.commands.append(tc.ADD_LABWARE(id=trash_can_id, descriptor=tc.TrashDescriptor()))
    script_a.commands.append(
        tc.ADD_PIPETTE_TIP_GROUP(
            id=pipette_tip_group_id_1,
            descriptor=tc.PipetteTipGroupDescriptor(
                row_count=channel_count,
                column_count=1,
            ),
        )
    )
    #  Actions
    script_a.commands.append(tc.RETRIEVE_TOOL(robot_id=robot_id, id=pipette_id))
    script_a.commands.append(
        tc.RETRIEVE_PIPETTE_TIP_GROUP(id=pipette_tip_group_id_1, robot_id=robot_id)
    )
    script_a.commands.append(tc.DISCARD_PIPETTE_TIP_GROUP(robot_id=robot_id))
    script_a.commands.append(tc.RETURN_TOOL(robot_id=robot_id))

    client = TCodeServicerClient(servicer_url=servicer_url)
    client.run_script(script_a)

    script_b = tc.TCodeScript.new(
        name=f"Pick up and Eject Tip (C1P{pipette_volume.magnitude}) - Part B",
    )
    script_b.commands.append(
        tc.ADD_PIPETTE_TIP_GROUP(
            id=pipette_tip_group_id_2,
            descriptor=tc.PipetteTipGroupDescriptor(
                row_count=channel_count,
                column_count=1,
            ),
        )
    )
    #  Actions
    script_b.commands.append(tc.RETRIEVE_TOOL(robot_id=robot_id, id=pipette_id))
    script_b.commands.append(
        tc.RETRIEVE_PIPETTE_TIP_GROUP(id=pipette_tip_group_id_2, robot_id=robot_id)
    )
    script_b.commands.append(tc.DISCARD_PIPETTE_TIP_GROUP(robot_id=robot_id))
    script_b.commands.append(tc.RETURN_TOOL(robot_id=robot_id))

    # @connor: This throws an error
    client.run_script(script_b, clean_environment=False)



if __name__ == "__main__":
    plac.call(main)
