from typing import Literal

from ..base import BaseRobotSpecificTCodeCommand


class RETURN_TOOL_V1(BaseRobotSpecificTCodeCommand):
    """Return the currently held tool to the tool rack."""

    type: Literal["RETURN_TOOL"] = "RETURN_TOOL"
    schema_version: Literal[1] = 1
