from typing import Literal

from ...common.docs import ToolIdField
from ..base import BaseRobotSpecificTCodeCommand


class RETRIEVE_TOOL_V1(BaseRobotSpecificTCodeCommand):
    """Pick up the target tool using the robot's empty flange."""

    type: Literal["RETRIEVE_TOOL"] = "RETRIEVE_TOOL"
    schema_version: Literal[1] = 1

    id: ToolIdField
