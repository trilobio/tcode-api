"""Code to manage compatibility between different versions of tcode-api.

The machinery lives in :mod:`py_organelles.schema_versioning`. This module contains:
    * ``tcode_api_compat_context``: mapping from tcode-api semantic version (e.g. 'v1.35.1') to
      individual schema versions (e.g. SEND_WEBHOOK -> v2, WAIT -> v3), and tcode-api's registries.
    * Wrappers of the ``py_organelles.schema_versioning`` functions, defaulting to
      ``tcode_api_compat_context``.
    * ``read_and_migrate_script`` to load and migrate a whole TCode script.

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

import importlib
import json
import logging
from typing import cast

from py_organelles import schema_versioning
from py_organelles.schema_versioning import (
    APIHistoryLog,
    APIVersion,
    BaseSchemaVersionedModel,
    CompatContext,
    DeprecatedSchemaError,
    InvalidDataError,
    SchemaName,
    SchemaVersion,
    SchemaVersionMismatchError,
    TargetSchemaExistsError,
    TargetSchemaNotFoundError,
)

from ..schemas.commands.union import TCode
from ..schemas.registry import RawData, migration_registry, schema_registry
from ..schemas.script.metadata.latest import Metadata
from ..schemas.script.tcode_script import TCodeScript

__all__ = [
    "APIHistoryLog",
    "APIVersion",
    "CompatContext",
    "DeprecatedSchemaError",
    "InvalidDataError",
    "SchemaName",
    "SchemaVersion",
    "SchemaVersionMismatchError",
    "TargetSchemaExistsError",
    "TargetSchemaNotFoundError",
    "load_api_object",
    "migrate_data_to_latest",
    "migrate_data_to_version",
    "read_and_migrate_script",
    "resolve_api_profile",
    "tcode_api_compat_context",
]

_logger = logging.getLogger(__name__)

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
            "v1.49.0": {
                "CALIBRATE_LABWARE_WELL_CENTER": 1,
            },
            "v1.50.0": {
                "ADD_MODULE": 1,
                "ModuleDescription": 1,
                "ModuleDescriptor": 1,
                "SEND_WEBHOOK": 2,
            },
            "v1.51.0": {
                "CREATE_LABWARE": 4,
                "ModuleId": 1,
                "PUT_DOWN_LABWARE": 2,
                "REGISTER_MODULE": 2,
                "REMOVE_LABWARE_LID": 3,
            },
        },
        migrations={
            "v1.37.0": {
                "CALIBRATE_TOOL_FOR_PROBING": "CALIBRATE_TOOL",
            },
            "v1.51.0": {
                "ADD_MODULE": "REGISTER_MODULE",
            },
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
    unversioned_is_v1: bool = False,
) -> RawData:
    """Migrate a given json blob to the latest version of its schema.

    Wraps :func:`py_organelles.schema_versioning.migrate_data_to_latest`, which documents the
    parameters, defaulting ``context`` to the tcode-api context.
    """
    return schema_versioning.migrate_data_to_latest(
        data,
        schema_name=schema_name,
        schema_version=schema_version,
        context=context,
        recurse=recurse,
        unversioned_is_v1=unversioned_is_v1,
    )


def migrate_data_to_version(
    data: RawData,
    target_version: int | None,
    schema_name: str | None = None,
    schema_version: int | None = None,
    context: CompatContext = tcode_api_compat_context,
    recurse: bool | None = None,
    unversioned_is_v1: bool = False,
) -> RawData:
    """Migrate a given json blob to the specified version of it's schema.

    Wraps :func:`py_organelles.schema_versioning.migrate_data_to_version`, which documents the
    parameters, defaulting ``context`` to the tcode-api context.
    """
    return schema_versioning.migrate_data_to_version(
        data,
        target_version,
        schema_name=schema_name,
        schema_version=schema_version,
        context=context,
        recurse=recurse,
        unversioned_is_v1=unversioned_is_v1,
    )


def load_api_object(
    data: RawData,
    api_version: str | None = None,
    context: CompatContext = tcode_api_compat_context,
    unversioned_is_v1: bool = False,
) -> BaseSchemaVersionedModel:
    """Given a data blob and the tcode-api version it corresponds to, return an instance of the most
        modern schema that the data can be migrated to.

    Wraps :func:`py_organelles.schema_versioning.load_api_object`, which documents the
    parameters, defaulting ``context`` to the tcode-api context.
    """
    return schema_versioning.load_api_object(
        data,
        api_version=api_version,
        context=context,
        unversioned_is_v1=unversioned_is_v1,
    )


def resolve_api_profile(
    api_version: APIVersion,
    context: CompatContext = tcode_api_compat_context,
) -> dict[SchemaName, SchemaVersion]:
    """Resolve a schema-version profile for the given API version.

    Wraps :func:`py_organelles.schema_versioning.resolve_api_profile`, which documents the
    parameters, defaulting ``context`` to the tcode-api context.
    """
    return schema_versioning.resolve_api_profile(api_version, context)


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
