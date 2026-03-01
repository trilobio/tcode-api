from typing import Annotated, Literal

from pydantic import Field

from ....base import BaseSchemaVersionedModel
from ....common.value_with_units import ValueWithUnits

OffsetField = Annotated[
    ValueWithUnits,
    Field(
        description="The distance from the base to tip of the conical portion of the well. expects length units",
    ),
]


class ConicalBottomDescriptionV1(BaseSchemaVersionedModel):
    """Description of a conical bottom well.

    :note: It is assumed that the conical portion of the well comes to a point at the bottom of the well
    """

    type: Literal["Conical"] = "Conical"
    schema_version: Literal[1] = 1

    offset: OffsetField


class ConicalBottomDescriptorV1(BaseSchemaVersionedModel):
    """:class:``ConicalBottomDescription`` with optional parameters."""

    type: Literal["Conical"] = "Conical"
    schema_version: Literal[1] = 1

    offset: OffsetField | None = None
