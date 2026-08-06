from typing import Literal

from ..base.tool_descriptor.v1 import BaseToolDescriptorV1


class GripperDescriptor(BaseToolDescriptorV1):
    type: Literal["Gripper"] = "Gripper"
    schema_version: Literal[1] = 1
