"""BaseSchemaVersionedModel v1."""

from abc import ABC

from py_organelles.schema_versioning import BaseSchemaVersionedModel

from ..configured_model.v1 import BaseConfiguredModelV1


class BaseSchemaVersionedModelV1(BaseConfiguredModelV1, BaseSchemaVersionedModel, ABC):
    """TCode-configured BaseModel with a schema_version field.

    ``schema_version``, ``read()``, and ``write()`` come from :class:`BaseSchemaVersionedModel`;
    this class adds TCode's configuration from :class:`BaseConfiguredModelV1`.
    """
