"""BaseDescriberWithTags v1."""

from abc import ABC

from pydantic import Field

from ....base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1
from ....common.docs import NamedTags, Tags


class BaseDescriberWithTagsV1(BaseSchemaVersionedModelV1, ABC):
    """Base schema shared by all models describing objects with tags and named_tags."""

    # default_factory fields duplicated here from ..common.docs to satisfy mypy
    tags: Tags = Field(default_factory=list)
    named_tags: NamedTags = Field(default_factory=dict)
