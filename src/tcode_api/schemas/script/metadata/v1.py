from typing import Literal

from pydantic import Field

from ...base import BaseSchemaVersionedModel


class MetadataV1(BaseSchemaVersionedModel):
    """TCode script metadata."""

    type: Literal["Metadata"] = "Metadata"
    schema_version: Literal[1] = 1

    name: str = Field(description="Script name")
    timestamp: str = Field(description="ISO 8601 timestamp of when the script was generated.")
    tcode_api_version: str = Field(description="tcode-api version used to generate this script.")
    description: str | None = Field(default=None, description="Script description")
