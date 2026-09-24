from typing import Literal

from ...base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1


class LabwareHolderDescriptor(BaseSchemaVersionedModelV1):
    """Descriptor for an entity that can hold labware."""

    type: Literal["LabwareHolder"] = "LabwareHolder"
    schema_version: Literal[1] = 1
