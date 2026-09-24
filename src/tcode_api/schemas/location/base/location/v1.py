"""BaseLocation v1."""

from pydantic import Field

from ....base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1


class BaseLocationV1(BaseSchemaVersionedModelV1):
    """Base schema shared by all locations in the Location discriminated union."""

    type: str = Field(
        description="Discriminator field, used to determine the specific location type."
    )
