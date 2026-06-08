import pathlib
import plac  # type: ignore [import-untyped]
import tcode_api.api as tc
from tcode_api.cli import (
    DEFAULT_SERVICER_URL,
    output_file_path_annotation,
    servicer_url_annotation,
)
from tcode_api.servicer import TCodeServicerClient
from tcode_api.utilities import create_transform, generate_id, mm, s


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
    for _ in range(10):
        script.commands.append(
            tc.MOVE_TO_LOCATION(
                robot_id=robot_id,
                location=tc.LocationRelativeToRobot(
                    robot_id=robot_id,
                    matrix=create_transform(x=mm(150), y=mm(150), z=mm(300))
                ),
                path_type=tc.PathType.DIRECT,
            )
        )
        script.commands.append(
            tc.WAIT(
                robot_id=robot_id,
                duration=s(3)
            )
        )
        script.commands.append(
            tc.MOVE_TO_LOCATION(
                robot_id=robot_id,
                location=tc.LocationRelativeToRobot(
                    robot_id=robot_id,
                    matrix=create_transform(x=mm(250), y=mm(250), z=mm(300))
                ),
                path_type=tc.PathType.DIRECT,
            )
        )
        script.commands.append(
            tc.WAIT(
                robot_id=robot_id,
                duration=s(3)
            )
        )

    if output_file_path is not None:
        with output_file_path.open("w") as f:
            script.write(f)
    client = TCodeServicerClient(servicer_url=servicer_url)
    client.run_script(script)


if __name__ == "__main__":
    plac.call(main)
