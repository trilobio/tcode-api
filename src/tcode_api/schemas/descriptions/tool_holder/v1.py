from typing import Literal

from ..base import BaseSchemaVersionedModel


class ToolHolderDescriptor(BaseSchemaVersionedModel):
    """Descriptor for an entity that can hold tools."""

    type: Literal["ToolHolder"] = "ToolHolder"
    schema_version: Literal[1] = 1
