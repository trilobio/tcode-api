"""Registry for schemas and corresponding migration functions."""

from typing import Any, Callable, Mapping, TypeVar, cast

from pydantic import ValidationError

from .base.schema_versioned_model.v1 import BaseSchemaVersionedModelV1

RegistryKey = str

RawData = Mapping[str, Any]
Migrator = Callable[[RawData], RawData]

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


class BuilderNotFoundError(Exception):
    """Exception raised when a builder is not found in the factory.

    :param factory_key: The key of the factory that was searched.
    :param builder_keys: The keys of the builders currently registered to the factory.
    """

    def __init__(
        self,
        factory_name: str,
        factory_key: RegistryKey,
        builder_keys: list[RegistryKey],
        message: str | None = None,
    ) -> None:
        if message is None:
            message = (
                f"{factory_name} has no builder registered with {factory_key}; "
                f"available builders: {', '.join(builder_keys)}"
            )
        self.factory_name = factory_name
        self.factory_key = factory_key
        self.builder_keys = builder_keys
        super().__init__(message)


class BuilderExistsError(Exception):
    """Exception raised when a builder is already registered in the factory.

    :param factory_key: The key of the factory that was searched.
    :param builder_keys: The keys of the builders currently registered to the factory.
    """

    def __init__(
        self, factory_key: RegistryKey, builder_keys: list[RegistryKey], msg: str | None = None
    ) -> None:
        self.factory_key = factory_key
        self.builder_keys = builder_keys
        super().__init__(msg)


class MigrationRegistry:
    """Registry for migration functions between different versions of tcode-api schemas."""

    def __init__(
        self, _migrators_to_preload: Mapping[str, Mapping[int, Migrator]] | None = None
    ) -> None:
        self._migrators: dict[RegistryKey, dict[int, Migrator]] = {}
        if _migrators_to_preload is not None:
            for key, migrations in _migrators_to_preload.items():
                for schema_version, migrator in migrations.items():
                    self.register_migrator(
                        key=key, schema_version=schema_version, migrator=migrator
                    )

    def get_migrators_for_schema(self, key: RegistryKey) -> dict[int, Migrator]:
        """Get all migration functions registered for a given schema key.

        :param key: The key representing the schema to retrieve migrations for.
        :returns: A mapping of schema versions to migration functions for the given schema key.
        :raises BuilderNotFoundError: If no migration functions are registered for the given schema key.
        """
        try:
            return self._migrators[key]
        except KeyError as err:
            raise BuilderNotFoundError(
                factory_name=self.__class__.__name__,
                factory_key=key,
                builder_keys=list(self._migrators.keys()),
            ) from err

    def register_migrator(
        self, key: RegistryKey, schema_version: int, migrator: Migrator, override: bool = False
    ) -> None:
        """Register a migration function to a specific `schema_version` of `key` in the registry.

        :param key: Name of the schema that is migrated by the `migrator`.
        :param schema_version: schema version that the `migrator` migrates to. Must be a positive
            integer > 0.
        :param migrator: Function that migrates a raw mapping of data from `schema_version` - 1
            compatibility to `schema_version` compatibility.
        :param override: Whether to override an existing migration function registered with the same
            `key` and `schema_version`. Defaults to False.

        :raises BuilderExistsError: If a migration function is already registered for the given keys.
        """
        if key not in self._migrators:
            self._migrators[key] = {}

        if not isinstance(schema_version, int) or schema_version <= 0:
            raise ValueError(f"schema_version must be a positive integer; got {schema_version}")

        if schema_version in self._migrators[key] and not override:
            raise BuilderExistsError(
                msg=(
                    f"{self.__class__.__name__} already has a registered migrator for {key} to schema version {schema_version}; "
                    "cannot register another"
                ),
                factory_key=f"{key} -> {schema_version}",
                builder_keys=[f"{k} -> {v}" for k, v in self._migrators[key].items()],
            )

        self._migrators[key][schema_version] = migrator


# using Mapping here instead of dict allows builders to accept more flexible dict-like types
# (e.g. pydantic's BaseModel, which is not a dict but implements Mapping)
BuilderFunc = Callable[[RawData], BaseSchemaVersionedModelV1]


class SchemaRegistry:
    """Registry for the latest constructors for all tcode-api schemas."""

    def __init__(
        self,
        _builders_to_preload: (
            dict[RegistryKey, type[BaseSchemaVersionedModelV1] | BuilderFunc] | None
        ) = None,
    ) -> None:
        """Initialize the registry with an optional mapping of keys to schema builders.

        :param _builders_to_preload: Optional mapping of keys to schema builders.
            pairs are passed sequentially to ``register()`` method during initialization.
            intended for unittest use to set up a test registry in a single line.
        """
        self._builders: dict[RegistryKey, BuilderFunc] = {}
        if _builders_to_preload is not None:
            for key, builder in _builders_to_preload.items():
                self.register(key=key, schema=builder)

    def register(
        self,
        key: str,
        schema: type[BaseSchemaVersionedModelV1] | BuilderFunc,
        override: bool = False,
    ) -> None:
        """Register a schema builder with the registry.

        :param key: The key to associate with the builder. Prefer to use the 'type' attribute
            value from the targeted schema, but can be customized if needed.
        :param schema: The schema or schema builder to register. If a schema is provided, that
            schema's `model_validate` method will be used as the builder. If a method is
            provided, it will be used directly.
        :param override: Whether to override an existing builder registered with the same key. Defaults to False.

        :raises BuilderExistsError: If a builder is already registered with the given key and override is not True.
        """
        if not override and key in self._builders:
            raise BuilderExistsError(
                msg=(
                    f"{self.__class__.__name__} already has a registered builder for {key}; "
                    "provide override=True to replace it"
                ),
                factory_key=key,
                builder_keys=list(self._builders.keys()),
            )

        if isinstance(schema, type):
            if issubclass(schema, BaseSchemaVersionedModelV1):
                builder: BuilderFunc = cast(BuilderFunc, schema.model_validate)
            else:
                raise TypeError(
                    f"Provided schema for {key} is a class but not a subclass of BaseSchemaVersionedModelV1; got {schema}"
                )
        else:
            builder = schema

        self._builders[key] = builder

    def get_builder(self, key: str) -> BuilderFunc:
        """Get the builder associated with the given key.

        :param key: The key associated with the builder to retrieve.
        :returns: The builder associated with the given key.
        :raises BuilderNotFoundError: If no builder is registered for the given key.
        """
        try:
            return self._builders[key]
        except KeyError as err:
            raise BuilderNotFoundError(
                factory_name=self.__class__.__name__,
                factory_key=key,
                builder_keys=list(self._builders.keys()),
            ) from err

    def build_instance(self, data: RawData, key: str | None = None) -> BaseSchemaVersionedModelV1:
        """Construct a relevant schema instance from the provided data.

        :param data: schema-compliant data from some version of the schema.
            Will be fed to pydantic.Model.validate_model() of the relevant schema version.
        :param key: optional key used to retrieve the builder from `get_builder()`. If not provided,
            the "type" field of the data will be used.

        :returns: Instance of the relevant schema version, constructed from the provided data.

        :raises ValueError: if the key is not provided and the "type" field is not present in the data
        :raises BuilderNotFoundError: if no builder is found for the provided key
        """
        if key is None:
            try:
                key = data["type"]
            except KeyError as err:
                raise ValueError(
                    "No key provided and 'type' field not found in data; cannot determine builder to use"
                ) from err
        builder = self.get_builder(data["type"])
        return builder(data)

    @property
    def keys(self) -> list[RegistryKey]:
        """Get a list of all keys currently registered in the registry."""
        return list(self._builders.keys())


migration_registry = MigrationRegistry()

schema_registry = SchemaRegistry()
