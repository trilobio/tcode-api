from typing import Literal

from ...common.docs import ToolIdField
from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class RETRIEVE_TOOL(BaseRobotSpecificTCodeCommandV1):
    """Pick up the target tool using the robot's empty flange."""

    type: Literal["RETRIEVE_TOOL"] = "RETRIEVE_TOOL"
    schema_version: Literal[1] = 1

    id: ToolIdField
