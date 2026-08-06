from typing import Literal

from ...base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1


class ToolHolderDescriptor(BaseSchemaVersionedModelV1):
    """Descriptor for an entity that can hold tools."""

    type: Literal["ToolHolder"] = "ToolHolder"
    schema_version: Literal[1] = 1
