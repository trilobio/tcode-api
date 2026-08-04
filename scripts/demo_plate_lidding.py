"""Demonstrate using a labware gripper to lid and un-lid lidded plates."""

import pathlib
from typing import cast

import plac  # type: ignore [import-untyped]

import tcode_api.api as tc
from tcode_api.cli import (
    DEFAULT_SERVICER_URL,
    output_file_path_annotation,
    robot_serial_number_annotation,
    servicer_url_annotation,
)
from tcode_api.servicer import TCodeServicerClient
from tcode_api.utilities import describe_well_plate, generate_id, load_labware


@plac.annotations(
    servicer_url=servicer_url_annotation,
    output_file_path=output_file_path_annotation,
    robot_sn=robot_serial_number_annotation,
)
def main(
    servicer_url: str = DEFAULT_SERVICER_URL,
    output_file_path: pathlib.Path | None = None,
    robot_sn: str | None = None,
) -> None:
    script = tc.TCodeScript.new(
        name=__file__,
        description=__doc__,
    )

    # FLEET
    robot_id, gripper_id = [generate_id() for _ in range(2)]
    script.commands.append(
        tc.ADD_ROBOT(id=robot_id, descriptor=tc.RobotDescriptor(serial_number=robot_sn))
    )
    script.commands.append(
        tc.ADD_TOOL(robot_id=robot_id, id=gripper_id, descriptor=tc.GripperDescriptor())
    )

    # LABWARE
    plate_count = 1
    script.commands.append(tc.COMMENT(text=f"Create {plate_count} lidded Thermo NUNC plates"))
    labware_ids = [generate_id() for _ in range(plate_count)]
    lid_ids = [generate_id() for _ in range(plate_count)]
    labware_holders = [
        tc.LabwareHolderName(robot_id=robot_id, name=f"DeckSlot_{i}") for i in (8, 9, 12)
    ][:plate_count]
    lid_holders = [
        tc.LabwareHolderName(robot_id=robot_id, name=f"DeckSlot_{i}") for i in (7, 10, 11)
    ][:plate_count]

    description = cast(tc.WellPlateDescription, load_labware("thermo_nunc_266120_plate"))
    lid_description = cast(tc.LidDescription, load_labware("thermo_nunc_266120_lid"))
    description.lid = lid_description
    for id, lid_id, holder in zip(labware_ids, lid_ids, labware_holders):
        script.commands.append(
            tc.CREATE_LABWARE(
                robot_id=robot_id,
                description=description,
                holder=holder,
            ),
        )
        script.commands += [
            tc.ADD_LABWARE(id=id, descriptor=describe_well_plate(has_lid=True), lid_id=lid_id)
        ]

    # ACTIONS #
    script.commands.append(tc.SWAP_TO_TOOL(robot_id=robot_id, id=gripper_id))

    i = 0
    script.commands += [
        tc.REMOVE_LABWARE_LID(
            robot_id=robot_id,
            labware_id=labware_ids[i],
            storage_holder=lid_holders[i],
        ),
        tc.REPLACE_LABWARE_LID(
            robot_id=robot_id,
            lid_id=lid_ids[i],
            labware_id=labware_ids[i],
        ),
    ]

    script.commands.append(tc.RETURN_TOOL(robot_id=robot_id))

    if output_file_path is not None:
        with output_file_path.open("w") as f:
            script.write(f)

    client = TCodeServicerClient(servicer_url=servicer_url)
    client.run_script(script)


if __name__ == "__main__":
    plac.call(main)
