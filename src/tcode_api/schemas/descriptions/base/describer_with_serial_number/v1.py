"""BaseDescriberWithSerialNumber v1."""

from abc import ABC

from pydantic import Field

from ....base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1


class BaseDescriberWithSerialNumberV1(BaseSchemaVersionedModelV1, ABC):
    """Base schema shared by all models describing objects identifiable by serial number."""

    serial_number: str | None = Field(
        default=None,
        description="Optional serial number - allows unique identification of a robot or tool.",
    )
