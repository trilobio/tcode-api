"""teach_point - Demonstrates teaching a Trilobot to move a plate between two locations.

Procedure:
    1. Run the script on a fleet with at least one Trilobot equipped with a gripper.
    2. The robot will swap to the gripper tool.
    3. The script will prompt you to teach one point. Grab the robot's flange and gently drag
         it to the first location (e.g., aligned to pick up a plate), then confirm the position.
    4. Repeat Step 2 for the second location (e.g., aligned to place the plate down).
    5. The robot will then autonomously move between the two taught points, picking up
         the plate from the first location and placing it at the second, then reversing the moves.
    6. The robot will return the gripper to the tool rack.
"""
import plac  # type: ignore [import-untyped]

import tcode_api.api as tc
from tcode_api.cli import (
    DEFAULT_SERVICER_URL,
    servicer_url_annotation,
)
from tcode_api.servicer import TCodeServicerClient
from tcode_api.utilities import generate_id


@plac.annotations(
    servicer_url=servicer_url_annotation,
)
def main(
    servicer_url: str = DEFAULT_SERVICER_URL,
) -> None:
    """CLI for the teach_point example script. See module docstring for full documentation."""
    script = tc.TCodeScript.new(
        name=__file__,
        description=__doc__,
    )

    # FLEET
    robot_id, gripper_id = [generate_id() for _ in range(2)]
    script.commands.append(tc.ADD_ROBOT(id=robot_id, descriptor=tc.RobotDescriptor()))
    script.commands.append(
        tc.ADD_TOOL(robot_id=robot_id, id=gripper_id, descriptor=tc.GripperDescriptor())
    )
    script.commands.append(
        tc.SWAP_TO_TOOL(robot_id=robot_id, id=gripper_id)
    )

    client = TCodeServicerClient(servicer_url=servicer_url)
    client.run_script(script)
    tf_a = client.teach_point(robot_id)
    print(tf_a)
    tf_b = client.teach_point(robot_id)
    print(tf_b)

    script_b = tc.TCodeScript.new(
        name=__file__,
        description=__doc__,
    )
    script_b.commands.append(
        tc.MOVE_GRIPPER(
            robot_id=robot_id,
            gripper_state_type=tc.GripperStateType.OPEN,
        ),
    )
    script_b.commands.append(
        tc.MOVE_TO_LOCATION(
            robot_id=robot_id,
            location=tc.LocationRelativeToWorld(matrix=tf_a),
        )
    )
    script_b.commands.append(
        tc.MOVE_GRIPPER(
            robot_id=robot_id,
            gripper_state_type=tc.GripperStateType.CLOSE,
        ),
    )
    script_b.commands.append(
        tc.MOVE_TO_LOCATION(
            robot_id=robot_id,
            location=tc.LocationRelativeToWorld(matrix=tf_b),
        )
    )
    script_b.commands.append(
        tc.MOVE_GRIPPER(
            robot_id=robot_id,
            gripper_state_type=tc.GripperStateType.OPEN,
        ),
    )
    script_b.commands.append(tc.SWAP_TO_TOOL(robot_id=robot_id, id=None))
    client.run_script(script_b, clean_environment=False)

if __name__ == "__main__":
    plac.call(main)
