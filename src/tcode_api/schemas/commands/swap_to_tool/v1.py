from typing import Literal

from ...common.docs import ToolIdField
from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class SWAP_TO_TOOL(BaseRobotSpecificTCodeCommandV1):
    """Return the currently held tool, then pick up the target tool."""

    type: Literal["SWAP_TO_TOOL"] = "SWAP_TO_TOOL"
    schema_version: Literal[1] = 1

    id: ToolIdField
