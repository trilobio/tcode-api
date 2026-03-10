from typing import Annotated, Literal

from pydantic import Field, PositiveInt

from ...base import BaseSchemaVersionedModel
from ...common.value_with_units import ValueWithUnits

RowCountField = Annotated[
    PositiveInt,
    Field(
        description="The number of rows in the grid.",
    ),
]

ColumnCountField = Annotated[
    PositiveInt,
    Field(
        description="The number of columns in the grid.",
    ),
]

RowPitchField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "The distance between the centers of adjacent rows in the grid. "
            "Expects length units."
        ),
    ),
]

ColumnPitchField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "The distance between the centers of adjacent columns in the grid. "
            "Expects length units."
        ),
    ),
]

RowOffsetField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "The offset distance from the grid's origin to the center of its parent, "
            "measured along the row axis. "
            "Modify this value when creating labware whose well grids aren't symmetric."
            "Expects length units."
        ),
    ),
]

ColumnOffsetField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "The offset distance from the grid's origin to the center of its parent, "
            "measured along the column axis. "
            "Modify this value when creating labware whose well grids aren't symmetric."
            "Expects length units."
        ),
    ),
]


class GridDescriptionV1(BaseSchemaVersionedModel):
    """Description of a grid layout."""

    type: Literal["Grid"] = "Grid"
    schema_version: Literal[1] = 1

    row_count: RowCountField
    column_count: ColumnCountField
    row_pitch: RowPitchField
    column_pitch: ColumnPitchField
    row_offset: RowOffsetField
    column_offset: ColumnOffsetField


class GridDescriptorV1(BaseSchemaVersionedModel):
    """:class:``GridDescription`` with optional parameters."""

    type: Literal["Grid"] = "Grid"
    schema_version: Literal[1] = 1

    row_count: RowCountField | None = None
    column_count: ColumnCountField | None = None
    row_pitch: RowPitchField | None = None
    column_pitch: ColumnPitchField | None = None
    row_offset: RowOffsetField | None = None
    column_offset: ColumnOffsetField | None = None
