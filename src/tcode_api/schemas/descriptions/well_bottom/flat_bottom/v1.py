from typing import Literal

from ....base import BaseSchemaVersionedModel


class FlatBottomDescriptorV1(BaseSchemaVersionedModel):
    """Descriptor for a flat bottom well."""

    type: Literal["Flat"] = "Flat"
    schema_version: Literal[1] = 1


class FlatBottomDescriptionV1(BaseSchemaVersionedModel):
    """:class:``FlatBottomDescription`` with optional paramters."""

    type: Literal["Flat"] = "Flat"
    schema_version: Literal[1] = 1
