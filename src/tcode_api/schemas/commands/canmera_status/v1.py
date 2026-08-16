from typing import Literal

from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class CANMERA_STATUS(BaseRobotSpecificTCodeCommandV1):
    """Log a CAN bus camera (canmera) node's health flags.

    Reports camera_ok / streaming / wifi_connected / robot_name_set / recording over
    the CAN bus, so it works before the node has any network access.
    """

    type: Literal["CANMERA_STATUS"] = "CANMERA_STATUS"
    schema_version: Literal[1] = 1
