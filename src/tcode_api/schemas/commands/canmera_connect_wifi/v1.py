from typing import Literal

from pydantic import Field

from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class CANMERA_CONNECT_WIFI(BaseRobotSpecificTCodeCommandV1):
    """Provision WiFi on a CAN bus camera (canmera) node and connect it.

    Runs over the CAN bus, so it works before the node has any network access. Once
    connected, the node's HTTP API is reachable (e.g. via SEND_WEBHOOK).
    """

    type: Literal["CANMERA_CONNECT_WIFI"] = "CANMERA_CONNECT_WIFI"
    schema_version: Literal[1] = 1

    ssid: str = Field(min_length=1, description="WiFi network name to join.")

    password: str = Field(min_length=8, description="WiFi password (WPA2 minimum length).")
