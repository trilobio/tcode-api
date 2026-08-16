from typing import Literal

from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class CANMERA_NET_STATUS(BaseRobotSpecificTCodeCommandV1):
    """Log a CAN bus camera (canmera) node's network status (SSID, hostname, IP).

    Runs over the CAN bus; use it to learn the node's address for HTTP control.
    """

    type: Literal["CANMERA_NET_STATUS"] = "CANMERA_NET_STATUS"
    schema_version: Literal[1] = 1
