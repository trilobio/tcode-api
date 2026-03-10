from typing import Annotated

from pydantic import Field

from .conical_bottom.latest import ConicalBottomDescription, ConicalBottomDescriptor
from .flat_bottom.latest import FlatBottomDescription, FlatBottomDescriptor
from .round_bottom.latest import RoundBottomDescription, RoundBottomDescriptor
from .v_bottom.latest import VBottomDescription, VBottomDescriptor

WellBottomShapeDescription = Annotated[
    ConicalBottomDescription | FlatBottomDescription | RoundBottomDescription | VBottomDescription,
    Field(
        discriminator="type",
        description="Union type of all valid well bottom shape descriptions.",
    ),
]
WellBottomShapeDescriptor = Annotated[
    ConicalBottomDescriptor | FlatBottomDescriptor | RoundBottomDescriptor | VBottomDescriptor,
    Field(
        discriminator="type",
        description="Union type of all valid well bottom shape descriptors.",
    ),
]
