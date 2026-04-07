from typing import Literal

from ..base import BasePipetteDescriptor


class SingleChannelPipetteDescriptor(BasePipetteDescriptor):
    type: Literal["SingleChannelPipette"] = "SingleChannelPipette"
    schema_version: Literal[1] = 1
