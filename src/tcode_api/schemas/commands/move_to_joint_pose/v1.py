from typing import Literal

from pydantic import Field

from ...common.value_with_units import ValueWithUnits
from ..base import BaseRobotSpecificTCodeCommand


class MOVE_TO_JOINT_POSE_V1(BaseRobotSpecificTCodeCommand):
    """Move the robot to the specified joint positions."""

    type: Literal["MOVE_TO_JOINT_POSE"] = "MOVE_TO_JOINT_POSE"
    schema_version: Literal[1] = 1

    joint_positions: list[ValueWithUnits] = Field(description="List of joint positions to move to.")

    relative: bool = Field(
        description=("Whether joint positions are relative to the current pose.")
    )
