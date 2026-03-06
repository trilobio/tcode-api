from __future__ import annotations

import datetime
import importlib.metadata
import logging
from typing import Literal, TextIO

from pydantic import Field

from ...base import BaseSchemaVersionedModel
from ...commands.union import TCode
from ..metadata.v1 import MetadataV1

_logger = logging.getLogger(__name__)


class TCodeScriptV1(BaseSchemaVersionedModel):
    """Structure of a TCode script."""

    type: Literal["TCodeScript"] = "TCodeScript"
    schema_version: Literal[1] = 1

    metadata: MetadataV1 = Field(
        description="Script metadata, significantly includeing the tcode-api version used in generation."
    )
    commands: list[TCode] = Field(
        default_factory=list,
        description="TCode commands in order of execution.",
    )

    @classmethod
    def new(cls, name: str, description: str | None = None) -> TCodeScriptV1:
        """Create a new, empty TCode script with the given name and optional description.

        :param name: Name of the TCode script.
        :param description: Optional description of the TCode script.

        :returns: A new, empty TCode script.
        """
        metadata = MetadataV1(
            name=name,
            description=description,
            timestamp=datetime.datetime.now().isoformat(),
            tcode_api_version=importlib.metadata.version("tcode_api"),
        )

        return cls(metadata=metadata, commands=[])

    @classmethod
    def read(cls, file_object: TextIO) -> TCodeScriptV1:
        """Load a TCode script from a file-like object.

        :param file_object: A file-like object containing the TCode script.

        :returns: The loaded TCode script.
        """
        model = super().read(file_object)
        current_version = importlib.metadata.version("tcode_api")
        if model.metadata.tcode_api_version != current_version:
            _logger.warning(
                "Loaded TCode script was created with API version %s, current version is %s",
                model.metadata.tcode_api_version,
                current_version,
            )
        return model
