from typing import Literal

from pydantic import Field

from ...common.value_with_units import ValueWithUnits
from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class MOVE_TO_JOINT_POSE(BaseRobotSpecificTCodeCommandV1):
    """Move the robot to the specified joint positions."""

    type: Literal["MOVE_TO_JOINT_POSE"] = "MOVE_TO_JOINT_POSE"
    schema_version: Literal[1] = 1

    joint_positions: list[ValueWithUnits] = Field(description="List of joint positions to move to.")

    relative: bool = Field(
        description=("Whether joint positions are relative to the current pose.")
    )
