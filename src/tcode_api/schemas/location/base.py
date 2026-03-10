"""Base classes for schemas representing physical locations in a fleet."""

from pydantic import Field

from ..base import BaseSchemaVersionedModel


class BaseLocation(BaseSchemaVersionedModel):
    """Base schema shared by all locations in the Location discriminated union."""

    type: str = Field(
        description="Discriminator field, used to determine the specific location type."
    )
