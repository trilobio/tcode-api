import pathlib
import numpy as np
import plac  # type: ignore [import-untyped]
import tcode_api.api as tc
from tcode_api.cli import (
    DEFAULT_SERVICER_URL,
    output_file_path_annotation,
    servicer_url_annotation,
)
from tcode_api.servicer import TCodeServicerClient
from tcode_api.utilities import create_transform, generate_id, mm, rad, s


@plac.annotations(
    servicer_url=servicer_url_annotation,
    output_file_path=output_file_path_annotation,
)
def main(
    servicer_url: str = DEFAULT_SERVICER_URL,
    output_file_path: pathlib.Path | None = None,
) -> None:
    script = tc.TCodeScript.new(
        name="joint space exploration",
    )
    robot_id = generate_id()
    script.commands.append(tc.ADD_ROBOT(id=robot_id, descriptor=tc.RobotDescriptor()))
    for j1 in np.linspace(0, np.pi*2, 200):
        for j3 in np.linspace(2.65, 1.7, 50):
                script.commands.append(
                    tc.MOVE_TO_JOINT_POSE(
                        robot_id=robot_id,
                        joint_positions= [
                             rad(j1),
                             mm(300),
                             rad(j3),
                             rad(1),
                        ],
                        relative=False,
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
