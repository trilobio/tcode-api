from typing import Literal

from ..base import BaseSchemaVersionedModel


class LabwareHolderDescriptorV1(BaseSchemaVersionedModel):
    """Descriptor for an entity that can hold labware."""

    type: Literal["LabwareHolder"] = "LabwareHolder"
    schema_version: Literal[1] = 1
