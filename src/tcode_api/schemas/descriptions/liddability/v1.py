from typing import Annotated, Literal

from pydantic import Field

from ...base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1
from ...common.value_with_units import ValueWithUnits
from ..labware.lid.v4 import LidDescription, LidDescriptor

LidOffsetField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "The offset from the top of the labware to the bottom of the lid. "
            "Expects length units. Only applicable if the labware has a lid."
        ),
    ),
]

lid_description = "Description of the lid, or None if the plate has no lid | is un-liddable."
supports_lid_description = (
    "Whether the labware supports a lid. If False, the lid and lid_offset fields will be ignored."
)


class LiddabilityDescription(BaseSchemaVersionedModelV1):
    """Description of whether and how a labware supports a lid."""

    type: Literal["Liddability"] = "Liddability"
    schema_version: Literal[1] = 1

    supports_lid: bool = Field(
        description=supports_lid_description,
    )
    lid_offset: LidOffsetField | None = None
    lid: LidDescription | None = Field(
        default=None,
        description=lid_description,
    )


class LiddabilityDescriptor(BaseSchemaVersionedModelV1):
    """:class:``LiddabilityDescription`` with optional parameters."""

    type: Literal["Liddability"] = "Liddability"
    schema_version: Literal[1] = 1

    supports_lid: bool | None = Field(
        default=None,
        description=supports_lid_description,
    )
    lid_offset: LidOffsetField | None = None
    lid: LidDescriptor | None = Field(
        default=None,
        description=lid_description,
    )
