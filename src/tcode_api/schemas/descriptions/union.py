from typing import Annotated

from pydantic import Field

from .axis_aligned_rectangle.latest import (
    AxisAlignedRectangleDescription,
    AxisAlignedRectangleDescriptor,
)
from .circle.latest import CircleDescription, CircleDescriptor

WellShapeDescription = Annotated[
    CircleDescription | AxisAlignedRectangleDescription,
    Field(
        discriminator="type",
        description="Union type of all valid well shape descriptions.",
    ),
]
WellShapeDescriptor = Annotated[
    CircleDescriptor | AxisAlignedRectangleDescriptor,
    Field(
        discriminator="type",
        description="Union type of all valid well shape descriptors.",
    ),
]
