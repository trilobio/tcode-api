from typing import Literal

from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class RETURN_TOOL(BaseRobotSpecificTCodeCommandV1):
    """Return the currently held tool to the tool rack."""

    type: Literal["RETURN_TOOL"] = "RETURN_TOOL"
    schema_version: Literal[1] = 1
