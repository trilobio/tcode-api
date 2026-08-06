from typing import Literal

from ..base.pipette_descriptor.v1 import BasePipetteDescriptorV1


class SingleChannelPipetteDescriptor(BasePipetteDescriptorV1):
    type: Literal["SingleChannelPipette"] = "SingleChannelPipette"
    schema_version: Literal[1] = 1
