from typing import Annotated, Literal

from pydantic import Field

from ...base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1
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


class AxisAlignedRectangleDescription(BaseSchemaVersionedModelV1):
    """Description of an axis-aligned rectangle."""

    type: Literal["AxisAlignedRectangle"] = "AxisAlignedRectangle"
    schema_version: Literal[1] = 1

    x_length: XLengthField
    y_length: YLengthField


class AxisAlignedRectangleDescriptor(BaseSchemaVersionedModelV1):
    """:class:``AxisAlignedRectangleDescription`` with optional parameters."""

    type: Literal["AxisAlignedRectangle"] = "AxisAlignedRectangle"
    schema_version: Literal[1] = 1

    x_length: XLengthField | None = None
    y_length: YLengthField | None = None
