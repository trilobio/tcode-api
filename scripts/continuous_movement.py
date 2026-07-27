"""Generate a tcode script to move the robot continuously for testing"""


from math import ceil

import numpy as np
import plac  # type: ignore [import-untyped]

import tcode_api.api as tc
from tcode_api.cli import (
    DEFAULT_SERVICER_URL,
    servicer_url_annotation,
)
from tcode_api.schemas.location.location_relative_to_robot import LocationRelativeToRobot
from tcode_api.servicer import TCodeServicerClient
from tcode_api.utilities import (
    create_transform,
    generate_id,
    m,
    rad,
)


@plac.annotations(
    servicer_url=servicer_url_annotation,
    number_of_commands=(
        "Number of TCode commands to generate approximately. Default is 27000. Each line takes approximately 2 seconds to run.",
        "option",
        "n",
        int,
    ),
)
def main(
    servicer_url: str = DEFAULT_SERVICER_URL,
    number_of_commands=30**3,
) -> None:
    """
    A simple script to generate MOVE_TO_LOCATION TCode commands for stress-testing
    the robot performance. It moves the robot within a safe radius below the tool rack.

    This script should only be ran when the robot isn't holding a tool.
    """
    points_per_axis = ceil(number_of_commands ** (1 / 3))

    space = []
    np.random.seed(3)
    x_range = np.linspace(-0.25, 0.25, points_per_axis)
    y_range = np.linspace(-0.25, 0.25, points_per_axis)
    z_range = np.linspace(0.15, 0.5, points_per_axis)

    for x in x_range:
        for y in y_range:
            # protect everything in radius 10cm from the origin
            if np.sqrt(x**2 + y**2) < 0.1:
                continue
            for z in z_range:
                space.append((x, y, z))
    print(
        f"Generated {len(space)} commands. Estimated run time is {round(len(space) * 2 / 60)} minutes"
    )
    np.random.shuffle(space)

    script = tc.TCodeScript.new(
        name="Stress test",
    )
    robot_id = generate_id()

    # Resolve robot and pipette
    script.commands.append(tc.ADD_ROBOT(id=robot_id, descriptor=tc.RobotDescriptor()))

    for x, y, z in space:
        script.commands.append(
            tc.MOVE_TO_LOCATION(
                robot_id=robot_id,
                path_type=tc.PathType.DIRECT,
                location=LocationRelativeToRobot(
                    robot_id=robot_id,
                    matrix=create_transform(m(x), m(y), m(z), rad(np.sin(x + y + z * np.pi))),
                ),
            )
        )

    client = TCodeServicerClient(
        servicer_url=servicer_url,
    )
    client.run_script(script, batch_process=True)


if __name__ == "__main__":
    plac.call(main)
