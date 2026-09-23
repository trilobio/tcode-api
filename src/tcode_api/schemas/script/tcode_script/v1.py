from __future__ import annotations

import datetime
import importlib.metadata
import json
import logging
from typing import Literal, TextIO, cast

from pydantic import Field

from ...base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1
from ...commands.union import TCode
from ..metadata.v1 import Metadata

_logger = logging.getLogger(__name__)


class TCodeScript(BaseSchemaVersionedModelV1):
    """Structure of a TCode script."""

    type: Literal["TCodeScript"] = "TCodeScript"
    schema_version: Literal[1] = 1

    metadata: Metadata = Field(
        description="Script metadata, significantly includeing the tcode-api version used in generation."
    )
    commands: list[TCode] = Field(
        default_factory=list,
        description="TCode commands in order of execution.",
    )

    @classmethod
    def new(cls, name: str, description: str | None = None) -> TCodeScript:
        """Create a new, empty TCode script with the given name and optional description.

        :param name: Name of the TCode script.
        :param description: Optional description of the TCode script.

        :returns: A new, empty TCode script.
        """
        metadata = Metadata(
            name=name,
            description=description,
            timestamp=datetime.datetime.now().isoformat(),
            tcode_api_version=importlib.metadata.version("tcode_api"),
        )

        return cls(metadata=metadata, commands=[])

    @classmethod
    def read(cls, file_object: TextIO) -> TCodeScript:
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

    @classmethod
    def read_and_migrate_to_latest(cls, json_str: str) -> TCodeScript:
        """Load a TCode script from a file-like object, and migrate it to the latest schema version.

        :param json_str: JSON as a string.

        :returns: The loaded TCode script.
        """

        # Import api from in here, to avoid a circular import.
        from ....api.compat import load_api_object  # noqa: PLC0415

        j = json.loads(json_str)

        api_version = j["metadata"]["tcode_api_version"]
        # Older scripts have no `type`/`schema_version` on the script, metadata, or commands, so
        # we can't migrate the whole script in one go. Instead, load each command individually,
        # resolving its schema version from the API version.
        commands: list[TCode] = []
        for c in j["commands"]:
            # load_api_object does the work of migration.
            commands.append(cast(TCode, load_api_object(c, api_version=api_version)))

        # Bump the script's overall version, since we've migrated every command in it.
        metadata = Metadata(**j["metadata"])
        metadata.tcode_api_version = importlib.metadata.version("tcode_api")

        script = TCodeScript(metadata=metadata, commands=commands)
        return script
