from typing import Literal

from ..base.tool_descriptor.v1 import BaseToolDescriptorV1


class ProbeDescriptor(BaseToolDescriptorV1):
    type: Literal["Probe"] = "Probe"
    schema_version: Literal[1] = 1
