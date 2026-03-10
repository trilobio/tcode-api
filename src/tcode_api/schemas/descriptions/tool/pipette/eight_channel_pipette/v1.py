from typing import Literal

from ..base import BasePipetteDescriptor


class EightChannelPipetteDescriptorV1(BasePipetteDescriptor):
    type: Literal["EightChannelPipette"] = "EightChannelPipette"
    schema_version: Literal[1] = 1
