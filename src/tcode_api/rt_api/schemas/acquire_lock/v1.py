from typing import Literal

from ..base.robot_serial_command.v1 import BaseRobotSerialCommandV1


class ACQUIRE_LOCK(BaseRobotSerialCommandV1):
    type: Literal["ACQUIRE_LOCK"] = "ACQUIRE_LOCK"
    schema_version: Literal[1] = 1
