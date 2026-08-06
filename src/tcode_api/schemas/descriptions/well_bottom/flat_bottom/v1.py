from typing import Literal

from ....base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1


class FlatBottomDescriptor(BaseSchemaVersionedModelV1):
    """Descriptor for a flat bottom well."""

    type: Literal["Flat"] = "Flat"
    schema_version: Literal[1] = 1


class FlatBottomDescription(BaseSchemaVersionedModelV1):
    """:class:``FlatBottomDescription`` with optional paramters."""

    type: Literal["Flat"] = "Flat"
    schema_version: Literal[1] = 1
