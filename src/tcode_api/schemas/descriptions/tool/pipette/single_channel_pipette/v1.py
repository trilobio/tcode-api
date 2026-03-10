from typing import Literal

from ..base import BasePipetteDescriptor


class SingleChannelPipetteDescriptorV1(BasePipetteDescriptor):
    type: Literal["SingleChannelPipette"] = "SingleChannelPipette"
    schema_version: Literal[1] = 1
