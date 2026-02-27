from typing import Annotated

from pydantic import Field

from .eight_channel_pipette.latest import EightChannelPipetteDescriptor
from .single_channel_pipette.latest import SingleChannelPipetteDescriptor

PipetteDescriptor = Annotated[
    SingleChannelPipetteDescriptor | EightChannelPipetteDescriptor,
    Field(discriminator="type", description="Union type of all valid Pipette descriptors."),
]
