from typing import Literal

from pydantic import Field

from ...common.value_with_units import ValueWithUnits
from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class MOVE_GRIPPER(BaseRobotSpecificTCodeCommandV1):
    """Manually drive the target robot's gripper."""

    type: Literal["MOVE_GRIPPER"] = "MOVE_GRIPPER"
    schema_version: Literal[1] = 1

    # note: cast as int to make TypeScript stuff not break
    gripper_state_type: int = Field(
        description=("Gripper state type; expects a value from :class:``GripperStateType``.")
    )

    finger_separation: ValueWithUnits | None = Field(
        default=None,
        description=("Desired finger separation distance when setting width."),
    )
