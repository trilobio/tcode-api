"""Registry for schemas and corresponding migration functions.

The registry classes live in :mod:`py_organelles.schema_versioning`. This module holds tcode-api's
instances of them, and helpers for tcode-api's Description/Descriptor schema pairs.
"""

from typing import TypeVar

from py_organelles.schema_versioning import (
    BuilderExistsError,
    BuilderFunc,
    BuilderNotFoundError,
    MigrationRegistry,
    Migrator,
    RawData,
    RegistryKey,
    SchemaRegistry,
)
from pydantic import ValidationError

from .base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1

__all__ = [
    "BuilderExistsError",
    "BuilderFunc",
    "BuilderNotFoundError",
    "DescriptionT",
    "DescriptorT",
    "MigrationRegistry",
    "Migrator",
    "RawData",
    "RegistryKey",
    "SchemaRegistry",
    "build_description_or_descriptor",
    "is_description_or_descriptor",
    "migration_registry",
    "schema_registry",
]

DescriptionT = TypeVar("DescriptionT", bound=BaseSchemaVersionedModelV1)
DescriptorT = TypeVar("DescriptorT", bound=BaseSchemaVersionedModelV1)


def is_description_or_descriptor(
    description_type: type[DescriptionT],
    descriptor_type: type[DescriptorT],
    data: RawData,
) -> tuple[bool, DescriptionT | DescriptorT]:
    """Build the fully-specified Description, falling back to the all-optional Descriptor.

    The fallback only triggers when ``description_type`` fails validation because required
    fields are missing from ``data`` -- any other validation failure (e.g. a cross-field
    validator rejecting an invalid combination of otherwise-present fields) propagates instead
    of being silently reinterpreted as "this must just be a partial/descriptor-style record".

    This function additionally returns a flag to allow re-use of the tested logic for determining
    if a data packet is a Description or Descriptor without needing to re-validate the data.

    :param description_type: The fully-specified schema class to try first.
    :param descriptor_type: The all-optional schema class to fall back to on missing fields.
    :param data: Raw data to validate.

    :returns: A tuple of the following:
        - True if the data is a Description, False if it is a Descriptor.
        - An instance of ``description_type``, or ``descriptor_type`` if ``data`` is missing
            fields required by ``description_type``.

    :raises ValidationError: If ``description_type`` fails for any reason other than missing
        fields.
    """
    try:
        return True, description_type.model_validate(data)
    except ValidationError as err:
        if all(error["type"] == "missing" for error in err.errors()):
            return False, descriptor_type.model_validate(data)
        raise


def build_description_or_descriptor(
    description_type: type[DescriptionT],
    descriptor_type: type[DescriptorT],
    data: RawData,
) -> DescriptionT | DescriptorT:
    """Build the fully-specified Description, falling back to the all-optional Descriptor.

    The fallback only triggers when ``description_type`` fails validation because required
    fields are missing from ``data`` -- any other validation failure (e.g. a cross-field
    validator rejecting an invalid combination of otherwise-present fields) propagates instead
    of being silently reinterpreted as "this must just be a partial/descriptor-style record".

    :param description_type: The fully-specified schema class to try first.
    :param descriptor_type: The all-optional schema class to fall back to on missing fields.
    :param data: Raw data to validate.

    :returns: An instance of ``description_type``, or ``descriptor_type`` if ``data`` is missing
        fields required by ``description_type``.

    :raises ValidationError: If ``description_type`` fails for any reason other than missing
        fields.
    """
    return is_description_or_descriptor(description_type, descriptor_type, data)[1]


migration_registry = MigrationRegistry()

schema_registry = SchemaRegistry()
