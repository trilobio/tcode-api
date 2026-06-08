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
    create_transform,
    describe_well_plate, 
    load_labware,
    generate_id,
    location_as_labware_index,
    m, 
    mm,
    rad, 
    s
)


@plac.annotations(
    servicer_url=servicer_url_annotation,
    output_file_path=output_file_path_annotation,
)
def main(
    servicer_url: str = DEFAULT_SERVICER_URL,
    output_file_path: pathlib.Path | None = None,
) -> None:

    script = tc.TCodeScript.new(
        name="minimal arm movement script",
    )
    robot_id = generate_id()
    script.commands.append(tc.ADD_ROBOT(id=robot_id, descriptor=tc.RobotDescriptor()))

    plate_id = generate_id()
    script.commands.append(
        tc.CREATE_LABWARE(
            robot_id=robot_id,
            description=load_labware("costar_3603_plate_hella_tall"),
            holder=tc.LabwareHolderName(robot_id=robot_id, name="DeckSlot_3"),
        )
    )
    script.commands.append(tc.ADD_LABWARE(id=plate_id, descriptor=describe_well_plate()))

    for well in range(96):
        script.commands.append(
            tc.MOVE_TO_LOCATION(
                robot_id=robot_id,
                location=location_as_labware_index(plate_id, well, tc.WellPartType.BOTTOM),
                path_type=tc.PathType.DIRECT,
            )
        )
        script.commands.append(
            tc.WAIT(
                robot_id=robot_id,
                duration=s(3)
            )
        )

    # for j1_mod, j3_mod in [(0,0), (-0.05,0), (-0.05,-0.05), (0,0)]:
    #     script.commands.append(
    #         tc.MOVE_TO_JOINT_POSE(
    #             robot_id=robot_id,
    #             joint_positions=[
    #                 rad(0.16) + rad(j1_mod),
    #                 m(0.300),
    #                 rad(2.0) + rad(j3_mod),
    #                 rad(1),
    #             ],
    #             relative=False
    #         )
    #     )
    #     script.commands.append(
    #         tc.WAIT(
    #             robot_id=robot_id,
    #             duration=s(3)
    #         )
    #     )

    if output_file_path is not None:
        with output_file_path.open("w") as f:
            script.write(f)
    client = TCodeServicerClient(servicer_url=servicer_url)
    client.run_script(script)


if __name__ == "__main__":
    plac.call(main)
