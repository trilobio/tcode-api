from typing import Literal

from pydantic import Field

from ..base import BaseDescriberWithSerialNumber
from ..labware_holder.v1 import LabwareHolderDescriptorV1
from ..tool.union import ToolDescriptor
from ..tool_holder.v1 import ToolHolderDescriptorV1


class RobotDescriptorV1(BaseDescriberWithSerialNumber):
    """Descriptor for a robot in the fleet."""

    type: Literal["Robot"] = "Robot"
    schema_version: Literal[1] = 1

    tools: dict[str, ToolDescriptor] = Field(
        default_factory=dict,
        description=(
            "list of tools currently attached to the robot, with their respective serial numbers (if any) as keys. "
            "Not currently used by the system, and will likely change before implementation. "
        ),
    )
    tool_holders: dict[str, ToolHolderDescriptorV1] = Field(
        default_factory=dict,
        description=(
            "list of tool holders currently attached to the robot, with their respective serial numbers (if any) as keys. "
            "Not currently used by the system, and will likely change before implementation. "
        ),
    )
    labware_holders: dict[str, LabwareHolderDescriptorV1] = Field(
        default_factory=dict,
        description=(
            "list of labware holders currently attached to the robot, with their respective serial numbers (if any) as keys. "
            "Not currently used by the system, and will likely change before implementation. "
        ),
    )
