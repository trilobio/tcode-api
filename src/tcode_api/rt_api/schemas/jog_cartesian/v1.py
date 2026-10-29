from typing import Literal

from pydantic import Field

from ....schemas.common.value_with_units import ValueWithUnits
from ....types import Matrix
from ..base.robot_serial_command.v1 import BaseRobotSerialCommandV1


class JOG_CARTESIAN(BaseRobotSerialCommandV1):
    type: Literal["JOG_CARTESIAN"] = "JOG_CARTESIAN"
    schema_version: Literal[1] = 1

    relative_pose: Matrix = Field(description="Pose to move to, relative to the current pose.")

    speed: ValueWithUnits | None = Field(
        default=None, description="Optional speed override applied only to this movement."
    )
