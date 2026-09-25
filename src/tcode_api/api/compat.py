"""Code to manage compatibiliy between different versions of tcode-api.

Comtains:
    * mapping from tcode-api semantic version (e.g. 'v1.35.1') to individual schema versions (e.g. SEND_WEBHOOK -> v2, WAIT -> v3)
    * ``_resolve_api_profile`` function to navigate the mapping.

How to perform:
    Rename:
        * Rename the schema in the BASE_PROFILE mapping to the new name.
        * Add an entry to API_RENAMES mapping the old name to the new name for the relevant APIVersion.

    Deprecate:
        * Remove the old command from the BASE_PROFILE mapping.
        * Add an entry to API_CHANGELOG with the new APIVersion mapping the old command name to the new command name.

    New:
        * Add the new command to the BASE_PROFILE mapping with the appropriate version number.

    REMOVE:
        * Remove the command from the BASE_PROFILE mapping.
        * Add an entry to API_REMOVALS with the removed command mapped to the APIVersion
"""

import collections.abc
import dataclasses
import importlib
import json
import logging
from typing import cast

from packaging.version import Version
from pydantic import ValidationError

from ..schemas.commands.union import TCode
from ..schemas.registry import (
    BuilderNotFoundError,
    MigrationRegistry,
    Migrator,
    RawData,
    SchemaRegistry,
    migration_registry,
    schema_registry,
)
from ..schemas.script.metadata.latest import Metadata
from ..schemas.script.tcode_script import TCodeScript

_logger = logging.getLogger(__name__)

APIVersion = str
SchemaVersion = int
SchemaName = str


@dataclasses.dataclass
class APIHistoryLog:
    """Data structure to track a given APIs evolution history."""

    name: str
    """API name (e.g. "tcode-api"), used for logging purposes."""

    increments: dict[APIVersion, dict[SchemaName, SchemaVersion]] = dataclasses.field(
        default_factory=dict
    )
    """Mapping of API versions to version increments of schemas in that version.

    Example:
        {
            "v0.1.0": {         # represents the initial supported release of the API
                "POUR_TEA": 1,
                "SMASH_CUP": 1,
                "TeaCup": 1,
            }
            "v0.1.1": {
                "POUR_TEA": 2,  # indicates that the ``POUR_TEA`` command was incremented to V2 in v0.1.1
                "TeaCup": 2,    # indicates that the ``TeaCup`` schema was incremented to V2 in v0.1.1
            },

            # Other versions may have been released, but because they didn't change the API,
            # they aren't represented in the changelog

            "v0.2.0": {
                "CoffeeCup": 1,  # indicates that the ``CoffeeCup`` schema was newly added in v0.2.0
                "POUR_COFFEE": 1,# indicates that the ``POUR_COFFEE`` command was newly added in v0.2.0
                "TeaCup": 3,     # indicates that the ``TeaCup`` schema was incremented to V3 in v0.2.0
        }
    """
    migrations: dict[APIVersion, dict[SchemaName, SchemaName | None]] = dataclasses.field(
        default_factory=dict
    )
    """Mapping of API versions to mappings of old schema names to new schema names.

    This functionality covers both renames (schema is the same but name changes) and replacements(schema is removed in favor of an existent schema).

    Example:
        {
            "v0.3.0": {
                "POUR_TEA": "POUR",  # indicates that the ``POUR_TEA`` command was replaced by ``POUR`` in v0.2.0
                "SMASH_CUP": None,   # indicates that the ``SMASH_CUP`` command was removed without replacement in v0.2.0
            }
        }
    """

    def get_most_recent_version(self) -> str:
        """Get the most recent API version in the history log."""
        return max(self.increments.keys(), key=Version)


@dataclasses.dataclass
class CompatContext:
    """Data structure unifying the state objects relevant for compatibility management.

    This gathers the various objects that must be swapped to unittest compatibility logic into a
        single place, and shouldn't need to be interacted with outside of test suites.
    """

    api_history_log: APIHistoryLog
    """The API history log to use for compatibility management."""

    migration_registry: MigrationRegistry
    """Registry of migrations between versions represented in ``api_history_log``."""

    schema_registry: SchemaRegistry
    """Registry of builders for schemas represented in the most modern version of the ``api_history_log``."""

    def known_schema_names(self) -> set[SchemaName]:
        names = set(self.schema_registry.keys)
        for renames in self.api_history_log.migrations.values():
            names.update(renames.keys())
        return names


class TargetSchemaNotFoundError(Exception):
    """Exception raised when a targeted schema is not found within in APIHistoryLog."""

    def __init__(
        self,
        schema_name: SchemaName,
        profile: dict[SchemaName, SchemaVersion],
        msg: str | None = None,
    ):
        if msg is None:
            msg = f"schema '{schema_name}' not valid within profile '{profile}'."
        super().__init__(msg)
        self.schema_name = schema_name
        self.profile = profile


class TargetSchemaExistsError(Exception):
    """Exception raised when a targeted schema already exists within in APIHistoryLog."""

    def __init__(
        self,
        schema_name: SchemaName,
        profile: dict[SchemaName, SchemaVersion],
        msg: str | None = None,
    ):
        if msg is None:
            msg = f"'{schema_name}' exists in '{profile}'."
        super().__init__(msg)
        self.schema_name = schema_name
        self.profile = profile


class InvalidDataError(ValueError):
    """Exception raised when data doesn't match schema expectations.

    Example cases include:
        * Missing 'type' key
        * 'schema_version' field doesn't match expected schema_version.
    """

    def __init__(self, data: RawData, msg: str | None = None):
        if msg is None:
            msg = f"Invalid data `{data}`"
        super().__init__(msg)
        self.data = data


class SchemaVersionMismatchError(Exception):
    """Exception raised on mismatching `schema_version` field in data and expected version from API."""

    def __init__(
        self,
        data: RawData,
        expected_schema_version: SchemaVersion,
        msg: str | None = None,
    ):
        if msg is None:
            msg = f"Expected schema version '{expected_schema_version}' but got '{data.get('schema_version')}' in data '{data}'."
        super().__init__(msg)
        self.data = data
        self.expected_schema_version = expected_schema_version


class DeprecatedSchemaError(Exception):
    """Exception raised when a schema is deprecated and cannot be migrated to the latest version."""

    def __init__(self, type: SchemaName, msg: str | None = None):
        if msg is None:
            msg = f"Schema '{type}' is deprecated in the latest tcode-api version and cannot be migrated."
        super().__init__(msg)
        self.type = type


tcode_api_compat_context = CompatContext(
    api_history_log=APIHistoryLog(
        name="tcode-api",
        increments={
            "v1.35.0": {
                "ADD_LABWARE": 1,
                "ADD_PIPETTE_TIP_GROUP": 1,
                "ADD_ROBOT": 1,
                "ADD_TOOL": 1,
                "ASPIRATE": 1,
                "AxisAlignedRectangleDescription": 1,
                "AxisAlignedRectangleDescriptor": 1,
                "CALIBRATE_LABWARE_HEIGHT": 1,
                "CALIBRATE_LABWARE_HOLDER": 1,
                "CALIBRATE_LABWARE_WELL_DEPTH": 1,
                "CALIBRATE_TOOL_FOR_PROBING": 1,
                "COMMENT": 1,
                "CREATE_LABWARE": 1,
                "CircleDescription": 1,
                "CircleDescriptor": 1,
                "ConicalBottomDescription": 1,
                "ConicalBottomDescriptor": 1,
                "DELETE_LABWARE": 1,
                "DISCARD_PIPETTE_TIP_GROUP": 1,
                "DISPENSE": 1,
                "EightChannelPipetteDescriptor": 1,
                "FlatBottomDescription": 1,
                "FlatBottomDescriptor": 1,
                "GridDescription": 1,
                "GridDescriptor": 1,
                "GripperDescriptor": 1,
                "LabwareHolderDescriptor": 1,
                "LabwareHolderName": 1,
                "LabwareId": 1,
                "LidDescription": 1,
                "LidDescriptor": 1,
                "LocationAsLabwareHolder": 1,
                "LocationAsLabwareIndex": 1,
                "LocationAsNodeId": 1,
                "LocationRelativeToCurrentPosition": 1,
                "LocationRelativeToLabware": 1,
                "LocationRelativeToRobot": 1,
                "LocationRelativeToWorld": 1,
                "MOVE_GRIPPER": 1,
                "MOVE_TO_JOINT_POSE": 1,
                "MOVE_TO_LOCATION": 1,
                "Metadata": 1,
                "PAUSE": 1,
                "PICK_UP_LABWARE": 1,
                "PICK_UP_PIPETTE_TIP": 1,
                "PUT_DOWN_LABWARE": 1,
                "PUT_DOWN_PIPETTE_TIP": 1,
                "PipetteDescriptor": 1,
                "PipetteTipBoxDescription": 1,
                "PipetteTipBoxDescriptor": 1,
                "PipetteTipDescription": 1,
                "PipetteTipDescriptor": 1,
                "PipetteTipGroupDescriptor": 1,
                "PipetteTipLayout": 1,
                "ProbeDescriptor": 1,
                "REMOVE_LABWARE_LID": 1,
                "REPLACE_LABWARE_LID": 1,
                "RETRIEVE_PIPETTE_TIP_GROUP": 1,
                "RETRIEVE_TOOL": 1,
                "RETURN_PIPETTE_TIP_GROUP": 1,
                "RETURN_TOOL": 1,
                "RobotDescriptor": 1,
                "RoundBottomDescription": 1,
                "RoundBottomDescriptor": 1,
                "SEND_WEBHOOK": 1,
                "SWAP_TO_TOOL": 1,
                "SingleChannelPipetteDescriptor": 1,
                "TCode": 1,
                "TCodeScript": 1,
                "ToolDescriptor": 1,
                "ToolHolderDescriptor": 1,
                "TrashDescription": 1,
                "TrashDescriptor": 1,
                "TubeDescription": 1,
                "TubeDescriptor": 1,
                "TubeHolderDescription": 1,
                "TubeHolderDescriptor": 1,
                "TubeRackDescription": 1,
                "TubeRackDescriptor": 1,
                "VBottomDescription": 1,
                "VBottomDescriptor": 1,
                "ValueWithUnits": 1,
                "WAIT": 1,
                "WellDescription": 1,
                "WellDescriptor": 1,
                "WellPlateDescription": 1,
                "WellPlateDescriptor": 1,
            },
            "v1.36.0": {
                "CREATE_LABWARE": 2,
            },
            "v1.36.2": {
                "ADD_LABWARE": 3,
                "CREATE_LABWARE": 3,
                "LidDescription": 3,
                "LidDescriptor": 3,
                "PipetteTipBoxDescription": 3,
                "PipetteTipBoxDescriptor": 3,
                "TrashDescription": 3,
                "TrashDescriptor": 3,
                "TubeHolderDescription": 3,
                "TubeHolderDescriptor": 3,
                "TubeRackDescription": 3,
                "TubeRackDescriptor": 3,
                "WellPlateDescription": 3,
                "WellPlateDescriptor": 3,
            },
            "v1.37.0": {
                "CALIBRATE_LABWARE_HEIGHT": 1,
                "CALIBRATE_TOOL": 1,
            },
            "v1.38.0": {
                "MOVE_TO_LOCATION": 2,
            },
            "v1.39.0": {
                "PAUSE": 2,
                "ADD_PIPETTE_TIP_GROUP": 2,
            },
            "v1.42.0": {
                "REMOVE_LABWARE_LID": 2,
                "REPLACE_LABWARE_LID": 2,
                "LidDescription": 4,
                "LidDescriptor": 4,
                "PipetteTipBoxDescription": 4,
                "PipetteTipBoxDescriptor": 4,
                "TrashDescription": 4,
                "TrashDescriptor": 4,
                "TubeHolderDescription": 4,
                "TubeHolderDescriptor": 4,
                "WellPlateDescription": 4,
                "WellPlateDescriptor": 4,
            },
            "v1.45.0": {
                "LiddabilityDescription": 1,
                "LiddabilityDescriptor": 1,
                "WellPlateDescription": 5,
                "WellPlateDescriptor": 5,
            },
            "v1.46.0": {
                "ADD_PIPETTE_TIP_GROUP": 3,
            },
        },
        migrations={
            "v1.37.0": {
                "CALIBRATE_TOOL_FOR_PROBING": "CALIBRATE_TOOL",
            }
        },
    ),
    migration_registry=migration_registry,
    schema_registry=schema_registry,
)


def migrate_data_to_latest(
    data: RawData,
    schema_name: str | None = None,
    schema_version: int | None = None,
    context: CompatContext = tcode_api_compat_context,
    recurse: bool = True,
) -> RawData:
    """Migrate a given json blob to the latest version of its schema.

    :param data: The json blob to migrate.
    :param schema_name: The name of the schema to migrate. If not provided, will attempt to infer
        from the 'type' key in the data.
    :param schema_version: The version of the schema to migrate. If not provided, will attempt to
        infer from the 'schema_version' key in the data.
    :param context: The targeted compatibility context. Defaults to the tcode-api context.
    :param recurse: Whether to migrate schemas nested inside this schema. Defaults to True.

    :returns: The migrated json blob, updated to match the latest version of the schema.
        If no migrators were found for the given schema, returns the data unchanged.

    :raises InvalidDataError: If the schema name or version cannot be inferred from the data and
        not provided as an argument.
    """
    return migrate_data_to_version(
        data=data,
        target_version=None,
        schema_name=schema_name,
        schema_version=schema_version,
        context=context,
        recurse=recurse,
    )


def migrate_data_to_version(
    data: RawData,
    target_version: int | None,
    schema_name: str | None = None,
    schema_version: int | None = None,
    context: CompatContext = tcode_api_compat_context,
    recurse: bool | None = None,
) -> RawData:
    """Migrate a given json blob to the specified version of it's schema.

    :param data: The json blob to migrate.
    :param version: The target version of the schema to migrate to. If not provided, will migrate to
        the latest version.
    :param schema_name: The name of the schema to migrate. If not provided, will attempt to infer
        from the 'type' key in the data.
    :param schema_version: The version of the schema to migrate. If not provided, will attempt to
        infer from the 'schema_version' key in the data.
    :param context: The targeted compatibility context. Defaults to the tcode-api context.
    :param recurse: Whether to migrate schemas nested inside this schema. Only possible when
        we're migrating to the newest version (target_version is None). Defaults to None, which sets
        it to True iff target_version is None.

    :returns: The migrated json blob, updated to match the specified version of the schema.
        If no migrators were found for the given schema, returns the data unchanged.

    :raises InvalidDataError: If any of the following are true:
        * the schema name or version cannot be inferred from the data and not provided as an
            argument.
        * the target version is older than the current version of the schema.
        * the target version has no registered migrator.

    """
    if recurse is None:
        recurse = target_version is None

    try:
        schema_name = schema_name or data["type"]
    except KeyError as err:
        raise InvalidDataError(
            msg="`schema_name` argument not supplied and no key 'type' in provided data",
            data=data,
        ) from err

    try:
        schema_version = schema_version or data["schema_version"]
    except KeyError as err:
        raise InvalidDataError(
            msg="`schema_version` argument not supplied and no key 'schema_version' in provided data",
            data=data,
        ) from err

    # Validate target version against current version
    if target_version is not None:
        if target_version == schema_version:
            return data  # No migration needed
        if target_version < schema_version:
            raise InvalidDataError(
                msg=f"Cannot migrate from version '{schema_version}' to version '{target_version}' for schema '{schema_name}' because the target version is older than the current version.",
                data=data,
            )

    try:
        final_name, migration_steps = _build_migrator_chain(
            incoming_name=schema_name,
            incoming_schema_version=schema_version,
            target_schema_version=target_version,
            context=context,
        )
    except ValueError as err:
        raise InvalidDataError(
            msg=f"Invalid migration path for data with type '{schema_name}' and schema_version '{schema_version}'.",
            data=data,
        ) from err

    if target_version is not None and target_version not in {v for _, v, _ in migration_steps}:
        raise InvalidDataError(
            msg=f"Cannot migrate from version '{schema_version}' to version '{target_version}' for schema '{schema_name}' because there is no registered migrator for the target version.",
            data=data,
        )

    for step_name, step_version, migrator in migration_steps:
        data = migrator(data)

    # Recurse, and migrate nested schemas.
    # We can only really do this if we're trying to migrate to the latest version.
    if recurse:
        if target_version is None:
            data = _migrate_nested_schemas_to_latest(context, data, skip_parent=True)
        else:
            raise RuntimeError("Can only migrate nested schemas to newest version")

    return {**data, "type": final_name}


def _migrate_nested_schemas_to_latest(
    context: CompatContext, data: RawData, skip_parent: bool = False
) -> RawData:
    """Recursively migrate nested schemas.

    Because we don't reliably track the versions of nested schemas, this just migrates
    everything to the newest version.

    Also: this currently only reads the schema version embedded in the data as `schema_version`. It
    doesn't figure out the schema version from the overall API version, as `migrate_data_to_version`
    does. So if there are old nested schemas that don't have versions, this isn't gonna catch them.
    This could be fixed, but not sure if worth the added complexity.

    :param context: The targeted compatibility context.
    :param data: JSON-like data to migrate.
    :param skip_parent: Don't migrate this object, only migrate nested ones.

    :returns: Data, migrated to newest versions.
    """

    if isinstance(data, list):
        return [_migrate_nested_schemas_to_latest(context, d) for d in data]
    if not isinstance(data, collections.abc.Mapping):
        return data

    if not skip_parent:
        if "schema_version" in data:
            if data.get("type") in context.known_schema_names():
                data = migrate_data_to_latest(
                    data=data,
                    # No schema_name, it should be inferrable.
                    schema_version=None,
                    context=context,
                    recurse=False,  # We're recursing out here, don't need to do it twice
                )
            else:
                # We don't yet migrate things that changed name. As of 2026-09-22, I
                # don't think we need to.
                _logger.warning("schema_version exists, but type isn't in schema_registry.")
        else:
            # It's not a nested schema, it's some other thing.
            pass

    return {k: _migrate_nested_schemas_to_latest(context, v) for k, v in data.items()}


def _resolve_api_profile(
    api_version: APIVersion,
    context: CompatContext = tcode_api_compat_context,
) -> dict[SchemaName, SchemaVersion]:
    """Resolve a schema-version profile for the given API version.

    :param api_version: The API version to resolve the profile for.
    :param context: The targeted compatibility context. Defaults to the tcode-api context.

    :returns: a mapping of schema names to their respective versions for the given API version,
        taking into account all changes up to that version.
    """
    requested = Version(api_version)

    profile: dict[SchemaName, SchemaVersion] = {}

    # Create sorted list of version strings that modified the API
    versions_of_note = sorted(
        set(context.api_history_log.increments.keys()).union(
            set(context.api_history_log.migrations.keys())
        ),
        key=Version,
    )
    for version_str in versions_of_note:
        # Check if we've got a modern enough version to return
        if Version(version_str) > requested:
            break

        # Handle increments
        if version_str in context.api_history_log.increments:
            for schema_name, schema_version in context.api_history_log.increments[
                version_str
            ].items():
                profile[schema_name] = schema_version

        # Handle migrations
        if version_str in context.api_history_log.migrations:
            for old_schema_name, new_schema_name in context.api_history_log.migrations[
                version_str
            ].items():
                if new_schema_name not in profile and new_schema_name is not None:
                    try:
                        profile[new_schema_name] = profile[old_schema_name]
                    except KeyError:
                        raise TargetSchemaNotFoundError(
                            schema_name=old_schema_name,
                            profile=profile,
                        )
                profile.pop(old_schema_name)

    return profile


def load_api_object(
    data: RawData,
    api_version: str | None = None,
    context: CompatContext = tcode_api_compat_context,
) -> object:
    """Given a data blob and the tcode-api version it corresponds to, return an instance of the most modern
        schema that the data can be migrated to.

    :param data: The mapping of data to load.
    :param api_version: The API version to resolve the schema profile against for loading.
        If not given, uses `type` and `schema_version` fields in the data to resolve the schema.
    :param context: The targeted compatibility context. Defaults to the tcode-api context.

    :returns: An instance of the most recent schema.

    :raises SchemaVersionMismatchError: If the schema_version targeted by the api_version doesn't match the
        schema_version of the provided data.
    :raises TargetSchemaNotFoundError: If the incoming data references a schema that doesn't exist in the
        API profile for the given api_version.
    :raises InvalidDataError: If the data is missing necessary keys to resolve the schema or
        doesn't match expected schema structure.
    :raises DeprecatedSchemaError: If the data references a schema that has been deprecated; only raised if
        no api_version argument provided.
    """
    try:
        incoming_name = data["type"]
        _logger.debug("data contains type='%s'", incoming_name)
    except KeyError as err:
        raise InvalidDataError(
            msg="Unable to find expected key 'type' in command schema",
            data=data,
        ) from err

    try:
        schema_version = data["schema_version"]
    except KeyError:
        schema_version = None
        if api_version is None:
            raise InvalidDataError(
                msg="No `schema_version` in data and no `api_version` provided to look up expected schema version.",
                data=data,
            )
        _logger.debug("No `schema_version` in data, looking up using `api_version`.")

    # If we didn't get a schema_version from the data, look it up with the API version.
    if api_version is not None:
        profile = _resolve_api_profile(api_version, context=context)
        if incoming_name not in profile:
            raise TargetSchemaNotFoundError(
                msg=f"Schema '{incoming_name}' not valid for API version '{api_version}'.",
                schema_name=incoming_name,
                profile=profile,
            )

        if schema_version is None:
            try:
                schema_version = profile[incoming_name]
            except KeyError:
                raise InvalidDataError(
                    msg=f"Data has no `schema_version`, and '{incoming_name}' is not valid for API version '{api_version}'.",
                    data=data,
                )

        if schema_version != profile[incoming_name]:
            raise SchemaVersionMismatchError(
                data=data,
                expected_schema_version=profile[incoming_name],
            )

    # Migrate data to the most recent accepted schema version for the incoming command.
    # `migrate_data_to_latest` follows renames and rewrites the "type" key to the final name.
    data = migrate_data_to_latest(
        data=data,
        schema_name=incoming_name,
        schema_version=schema_version,
        context=context,
    )
    new_name = data["type"]

    try:
        return context.schema_registry.build_instance(data=data, key=new_name)
    except ValidationError as err:
        raise InvalidDataError(
            msg=f"Data failed validation against schema '{new_name}' version '{schema_version}'.",
            data=data,
        ) from err


MigrationStep = tuple[
    SchemaName, SchemaVersion, Migrator
]  # (name the migrator belongs to, version it migrates *to*, fn)


def _build_migrator_chain(
    incoming_name: SchemaName,
    incoming_schema_version: SchemaVersion,
    target_schema_version: SchemaVersion | None = None,
    context: CompatContext = tcode_api_compat_context,
) -> tuple[SchemaName, list[MigrationStep]]:
    """Helper function to fetch all migrators necessary to migrate data from one schema_version to another, handling renames.

    :param incoming_name: The original name of the schema to migrate.
        if 'Teacup' was renamed to 'Cup' in a later version, provide 'Teacup'.
    :param incoming_schema_version: The version of the schema to migrate from.
    :param target_schema_version: The version of the schema to migrate to. If not provided, migrates
        to the latest version.
    :param context: The targeted compatibility context. Defaults to the tcode-api context.

    :returns: The most recent name of the target schema and a list of migrator functions to apply in order.

    :raises ValueError: If there is a gap in the migration path (e.g. no migrator from v1 to v2, but
        there is a migrator from v2 to v3).
    :raises DeprecatedSchemaError: If the target schema is deprecated and cannot be migrated to the latest version.
    """
    migrators_to_apply: list[MigrationStep] = []

    current_name = incoming_name
    current_version = incoming_schema_version

    continue_traversing: bool = True
    while continue_traversing:
        # Fetch and sequentially store all migrators for current_name starting at current_version.
        try:
            migrators = context.migration_registry.get_migrators_for_schema(current_name)
        except BuilderNotFoundError:
            migrators = {}

        for version in sorted(migrators.keys()):
            if (target_schema_version is not None) and (target_schema_version <= current_version):
                break

            if version - current_version > 1:
                raise ValueError(
                    f"Cannot migrate from version '{current_version}' to version '{version}' for schema '{current_name}' because there is a gap in the migration path. Missing migrator for version '{current_version + 1}'."
                )

            # Only check for version on the input name. For all other names, we need to walk the entire version tree
            if current_name == incoming_name and version <= current_version:
                continue
            _logger.debug(
                "Adding migrator for '%s' from v%d to v%d to migrator chain",
                current_name,
                current_version,
                version,
            )
            migrators_to_apply.append((current_name, version, migrators[version]))
            current_version = version

        if target_schema_version is not None and current_version >= target_schema_version:
            break  # reached the target; don't follow renames past it

        # Check for renames in the API history log and update the current_name accordingly
        continue_traversing = False  # Set back to true if we find a rename
        for api_version_str in sorted(context.api_history_log.migrations, key=Version):
            for schema_name in context.api_history_log.migrations[api_version_str]:
                if schema_name == current_name:
                    new_name = context.api_history_log.migrations[api_version_str][schema_name]
                    if new_name is None:
                        raise DeprecatedSchemaError(type=schema_name)

                    current_name = new_name
                    _logger.debug(
                        "Found rename of '%s' to '%s' in API version '%s'",
                        schema_name,
                        current_name,
                        api_version_str,
                    )
                    continue_traversing = True
                    break
            if continue_traversing:
                break

    return current_name, migrators_to_apply


def read_and_migrate_script(json_str: str) -> TCodeScript:
    """Load a TCode script from a file-like object, and migrate it to the latest schema version.

    :param json_str: JSON as a string.

    :returns: The loaded TCode script.
    """

    j = json.loads(json_str)

    api_version = j["metadata"]["tcode_api_version"]
    # Older scripts have no `type`/`schema_version` on the script, metadata, or commands, so
    # we can't migrate the whole script in one go. Instead, load each command individually,
    # resolving its schema version from the API version.
    commands: list[TCode] = []
    for c in j["commands"]:
        # load_api_object does the work of migration.
        commands.append(cast(TCode, load_api_object(c, api_version=api_version)))

    metadata = Metadata(**j["metadata"])
    # Bump the script's overall version, since we've migrated every command in it.
    new_api_version = importlib.metadata.version("tcode_api")
    if metadata.tcode_api_version != new_api_version:
        _logger.info(
            f"Bumping script's tcode API version from {metadata.tcode_api_version} to {new_api_version}"
        )
        metadata.tcode_api_version = new_api_version

    script = TCodeScript(metadata=metadata, commands=commands)
    return script
