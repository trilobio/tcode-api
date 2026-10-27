from typing import Literal

from ..base.robot_serial_command.v1 import BaseRobotSerialCommandV1


class RELEASE_LOCK(BaseRobotSerialCommandV1):
    type: Literal["RELEASE_LOCK"] = "RELEASE_LOCK"
    schema_version: Literal[1] = 1
