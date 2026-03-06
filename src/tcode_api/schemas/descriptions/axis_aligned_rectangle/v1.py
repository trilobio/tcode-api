from typing import Annotated, Literal

from pydantic import Field

from ...base import BaseSchemaVersionedModel
from ...common import ValueWithUnits

XLengthField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "The length of the rectangle along the X-axis of the parent object's coordinate system. expects length units."
        ),
    ),
]

YLengthField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "The length of the rectangle along the Y-axis of the parent object's coordinate system. expects length units."
        ),
    ),
]


class AxisAlignedRectangleDescriptionV1(BaseSchemaVersionedModel):
    """Description of an axis-aligned rectangle."""

    type: Literal["AxisAlignedRectangle"] = "AxisAlignedRectangle"
    schema_version: Literal[1] = 1

    x_length: XLengthField
    y_length: YLengthField


class AxisAlignedRectangleDescriptorV1(BaseSchemaVersionedModel):
    """:class:``AxisAlignedRectangleDescription`` with optional parameters."""

    type: Literal["AxisAlignedRectangle"] = "AxisAlignedRectangle"
    schema_version: Literal[1] = 1

    x_length: XLengthField | None = None
    y_length: YLengthField | None = None
