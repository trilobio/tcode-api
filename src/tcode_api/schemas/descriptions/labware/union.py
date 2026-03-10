from typing import Annotated

from pydantic import Field

from .lid.latest import LidDescription, LidDescriptor
from .pipette_tip_box.latest import PipetteTipBoxDescription, PipetteTipBoxDescriptor
from .trash.latest import TrashDescription, TrashDescriptor
from .tube_holder.latest import TubeHolderDescription, TubeHolderDescriptor
from .well_plate.latest import WellPlateDescription, WellPlateDescriptor

LabwareDescription = Annotated[
    LidDescription
    | PipetteTipBoxDescription
    | TrashDescription
    | TubeHolderDescription
    | WellPlateDescription,
    Field(
        discriminator="type",
        description="Union type of all valid labware descriptions.",
    ),
]
LabwareDescriptor = Annotated[
    LidDescriptor
    | PipetteTipBoxDescriptor
    | TrashDescriptor
    | TubeHolderDescriptor
    | WellPlateDescriptor,
    Field(
        discriminator="type",
        description="Union type of all valid labware descriptors.",
    ),
]
