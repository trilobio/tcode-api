from typing import Annotated, Literal

from pydantic import Field

from ...base import BaseSchemaVersionedModel
from ...common.value_with_units import ValueWithUnits

DiameterField = Annotated[
    ValueWithUnits,
    Field(
        description=("Maximum distance across the circle. " "expects length units"),
    ),
]


class CircleDescriptionV1(BaseSchemaVersionedModel):
    """Description of a circle."""

    schema_version: Literal[1] = 1
    type: Literal["Circle"] = "Circle"

    diameter: DiameterField


class CircleDescriptorV1(BaseSchemaVersionedModel):
    """CircleDescription with optional parameters."""

    type: Literal["Circle"] = "Circle"
    schema_version: Literal[1] = 1

    diameter: DiameterField | None = None
