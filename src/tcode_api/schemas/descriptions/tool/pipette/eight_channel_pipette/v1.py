from typing import Literal

from ..base.pipette_descriptor.v1 import BasePipetteDescriptorV1


class EightChannelPipetteDescriptor(BasePipetteDescriptorV1):
    type: Literal["EightChannelPipette"] = "EightChannelPipette"
    schema_version: Literal[1] = 1
