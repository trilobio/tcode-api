from typing import Literal

from ..base import BasePipetteDescriptor


class EightChannelPipetteDescriptor(BasePipetteDescriptor):
    type: Literal["EightChannelPipette"] = "EightChannelPipette"
    schema_version: Literal[1] = 1
