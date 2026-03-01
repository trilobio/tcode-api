from typing import Literal

from ..base import BaseToolDescriptor


class ProbeDescriptorV1(BaseToolDescriptor):

    type: Literal["Probe"] = "Probe"
    schema_version: Literal[1] = 1
