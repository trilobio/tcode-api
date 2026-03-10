from abc import ABC

from pydantic import Field

from ..base import BaseSchemaVersionedModel
from ..common.docs import NamedTags, Tags


class BaseDescriberWithSerialNumber(BaseSchemaVersionedModel, ABC):
    """Base schema shared by all models describing objects identifiable by serial number."""

    serial_number: str | None = Field(
        default=None,
        description="Optional serial number - allows unique identification of a robot or tool.",
    )


class BaseDescriberWithTags(BaseSchemaVersionedModel, ABC):
    """Base schema shared by all models describing objects with tags and named_tags."""

    # default_factory fields duplicated here from ..common.docs to satisfy mypy
    tags: Tags = Field(default_factory=list)
    named_tags: NamedTags = Field(default_factory=dict)
