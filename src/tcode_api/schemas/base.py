"""Base pydantic models shared by all TCode data structures.

These models are fundamental, and as such not schema-versioned.
As such, changes to these models is a fundamental breaking change.
"""

from abc import ABC
from typing import Self, TextIO

from pydantic import BaseModel, ConfigDict


class BaseConfiguredModel(BaseModel, ABC):
    """pydantic.BaseModel with configuration to apply to all TCode data structures.

    All TCode data structures should inherit from this class to ensure consistent
    configuration.
    """

    model_config = ConfigDict(strict=True, extra="ignore")


class BaseSchemaVersionedModel(BaseConfiguredModel, ABC):
    """TCode-configured BaseModel with a schema_version field.

    :note: ``read()`` and ``write()`` methods are exposed on this class because
    only schema-versioned models should be read from and written to JSON blobs.
    """

    schema_version: int

    @classmethod
    def read(cls, file_object: TextIO) -> Self:
        """Load a model from a file-like object.

        :param file_object: A file-like object (typically created via ``open('r')``).

        :returns: The loaded model.
        """
        data = file_object.read()
        return cls.model_validate_json(data)

    def write(self, file_object: TextIO) -> None:
        """Write the model to a file-like object.

        :param file_object: A file-like object (typically created via ``open('w')``).
        """
        data = self.model_dump_json(indent=2)
        file_object.write(data)
