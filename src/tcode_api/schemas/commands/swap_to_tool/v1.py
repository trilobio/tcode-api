from typing import Literal

from ...common.docs import ToolIdField
from ..base import BaseRobotSpecificTCodeCommand


class SWAP_TO_TOOL_V1(BaseRobotSpecificTCodeCommand):
    """Return the currently held tool, then pick up the target tool."""

    type: Literal["SWAP_TO_TOOL"] = "SWAP_TO_TOOL"
    schema_version: Literal[1] = 1

    id: ToolIdField
