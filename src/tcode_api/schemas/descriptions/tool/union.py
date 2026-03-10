from typing import Annotated

from pydantic import Field

from .gripper.latest import GripperDescriptor
from .pipette.eight_channel_pipette.latest import EightChannelPipetteDescriptor
from .pipette.single_channel_pipette.latest import SingleChannelPipetteDescriptor
from .probe.latest import ProbeDescriptor

ToolDescriptor = Annotated[
    SingleChannelPipetteDescriptor
    | EightChannelPipetteDescriptor
    | ProbeDescriptor
    | GripperDescriptor,
    Field(discriminator="type", description="Union type of all valid tool descriptors."),
]
