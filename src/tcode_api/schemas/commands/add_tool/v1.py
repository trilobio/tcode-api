from typing import Literal

from pydantic import Field

from ...descriptions.tool.union import ToolDescriptor
from ..base import BaseRobotSpecificTCodeCommand


class ADD_TOOL_V1(BaseRobotSpecificTCodeCommand):
    """Find a matching tool on the fleet and assign it the given id."""

    type: Literal["ADD_TOOL"] = "ADD_TOOL"
    schema_version: Literal[1] = 1

    id: str = Field(
        description=(
            "Identifier to assign to the resolved tool. "
            "This id is used in subsequent commands to reference this tool."
        )
    )

    descriptor: ToolDescriptor = Field(
        description="Minimal descriptor of the desired tool; resolved on the fleet."
    )
