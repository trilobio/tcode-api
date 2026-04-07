from typing import Literal

from ....base import BaseSchemaVersionedModel


class FlatBottomDescriptor(BaseSchemaVersionedModel):
    """Descriptor for a flat bottom well."""

    type: Literal["Flat"] = "Flat"
    schema_version: Literal[1] = 1


class FlatBottomDescription(BaseSchemaVersionedModel):
    """:class:``FlatBottomDescription`` with optional paramters."""

    type: Literal["Flat"] = "Flat"
    schema_version: Literal[1] = 1
