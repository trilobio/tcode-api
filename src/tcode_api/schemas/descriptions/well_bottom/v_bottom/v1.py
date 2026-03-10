from typing import Annotated, Literal

from pydantic import Field

from ....base import BaseSchemaVersionedModel
from ....common.value_with_units import ValueWithUnits

DirectionField = Annotated[
    Literal["x-axis", "y-axis"],
    Field(
        description="The axis of the well's coordinate system along which the spine of the V runs.",
    ),
]

OffsetField = Annotated[
    ValueWithUnits,
    Field(
        description="The height of the triangular portion of the well. Expects length units.",
    ),
]


class VBottomDescriptionV1(BaseSchemaVersionedModel):
    """Description of a V-bottom well (e.g. trough)."""

    type: Literal["V-Shape"] = "V-Shape"
    schema_version: Literal[1] = 1

    direction: DirectionField
    offset: OffsetField


class VBottomDescriptorV1(BaseSchemaVersionedModel):
    """:class:``VBottomDescription`` with optional parameters."""

    type: Literal["V-Shape"] = "V-Shape"
    schema_version: Literal[1] = 1

    direction: DirectionField | None = None
    offset: OffsetField | None = None
