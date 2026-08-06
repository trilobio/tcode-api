from typing import Annotated, Literal

from pydantic import Field

from ...base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1
from ...common.value_with_units import ValueWithUnits

DiameterField = Annotated[
    ValueWithUnits,
    Field(
        description=("Maximum distance across the circle. expects length units"),
    ),
]


class CircleDescription(BaseSchemaVersionedModelV1):
    """Description of a circle."""

    schema_version: Literal[1] = 1
    type: Literal["Circle"] = "Circle"

    diameter: DiameterField


class CircleDescriptor(BaseSchemaVersionedModelV1):
    """CircleDescription with optional parameters."""

    type: Literal["Circle"] = "Circle"
    schema_version: Literal[1] = 1

    diameter: DiameterField | None = None
