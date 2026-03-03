"""Code to manage compatibiliy between different versions of tcode-api.

Comtains:
    * mapping from tcode-api semantic version (e.g. 'v1.35.1') to individual schema versions (e.g. SEND_WEBHOOK -> v2, WAIT -> v3)
    * ``resolve_api_profile`` function to navigate the mapping.

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

import dataclasses

from packaging.version import Version

APIVersion = str
SchemaVersion = int
SchemaName = str


@dataclasses.dataclass
class APIHistoryLog:
    """Data structure to track a given APIs evolution history."""

    name: str
    """API name (e.g. "tcode-api"), used for logging purposes."""

    increments: dict[APIVersion, dict[SchemaName, SchemaVersion | None]] = dataclasses.field(
        default_factory=dict
    )
    """Mapping of API versions to version increments and removals of schemas in that version.

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
                "SMASH_CUP": None,# indicates that the ``SMASH_CUP`` command (thankfully) was removed in v0.2.0
        }
    """
    renames: dict[APIVersion, dict[SchemaName, SchemaName]] = dataclasses.field(
        default_factory=dict
    )
    """Mapping of API versions to mappings of old schema names to new schema names.

    Example:
        {
            "v0.3.0": {
                "POUR_TEA": "POUR",  # indicates that the ``POUR_TEA`` command was renamed to ``POUR`` in v0.2.0
            }
        }
    """

    replacements: dict[APIVersion, dict[SchemaName, SchemaName]] = dataclasses.field(
        default_factory=dict
    )
    """Mapping of API versions to mappings of deprecated schema names to their replacements.

    Example:
        {
            "v0.3.0": {
                "POUR_COFFEE": "POUR",  # indicates that the ``POUR_COFFEE`` command was replaced
            },                          # by the ``POUR`` command in v0.3.0
        }
    """


class TargetSchemaNotFoundError(Exception):
    """Exception raised when a targeted schema is not found within in APIHistoryLog."""


class TargetSchemaExistsError(Exception):
    """Exception raised when a targeted schema already exists within in APIHistoryLog."""

    schema_name: SchemaName


class InvalidSchemaError(Exception):
    """Exception raised on detection of an invalid schema.

    Example cases include:
        * Missing 'type' key
        * 'schema_version' field doesn't match expected fields.
    """

    bad_schema: dict


TCodeAPIHistory = APIHistoryLog(
    name="tcode-api",
    increments={
        "v1.35.0": {
            "ADD_LABWARE": 1,
            "ADD_PIPETTE_TIP_GROUP": 1,
            "ADD_ROBOT": 1,
            "ADD_TOOL": 1,
            "ASPIRATE": 1,
            "CALIBRATE_LABWARE_HEIGHT": 1,
            "CALIBRATE_LABWARE_WELL_DEPTH": 1,
            "CALIBRATE_TOOL_FOR_PROBING": 1,
            "COMMENT": 1,
            "CREATE_LABWARE": 1,
            "DELETE_LABWARE": 1,
            "DISCARD_PIPETTE_TIP_GROUP": 1,
            "DISPENSE": 1,
            "MOVE_GRIPPER": 1,
            "MOVE_TO_JOINT_POSE": 1,
            "MOVE_TO_LOCATION": 1,
            "PAUSE": 1,
            "PICK_UP_LABWARE": 1,
            "PICK_UP_PIPETTE_TIP": 1,
            "PUT_DOWN_LABWARE": 1,
            "PUT_DOWN_PIPETTE_TIP": 1,
            "REMOVE_LABWARE_LID": 1,
            "REPLACE_LABWARE_LID": 1,
            "RETRIEVE_PIPETTE_TIP_GROUP": 1,
            "RETRIEVE_TOOL": 1,
            "RETURN_PIPETTE_TIP_GROUP": 1,
            "RETURN_TOOL": 1,
            "SEND_WEBHOOK": 1,
            "SWAP_TO_TOOL": 1,
            "WAIT": 1,
            "Metadata": 1,
            "TCode": 1,
            "TCodeScript": 1,
            "ValueWithUnits": 1,
            "EightChannelPipetteDescriptor": 1,
            "GripperDescriptor": 1,
            "LabwareHolderDescriptor": 1,
            "PipetteDescriptor": 1,
            "ProbeDescriptor": 1,
            "RobotDescriptor": 1,
            "SingleChannelPipetteDescriptor": 1,
            "ToolDescriptor": 1,
            "ToolHolderDescriptor": 1,
            "AxisAlignedRectangleDescription": 1,
            "AxisAlignedRectangleDescriptor": 1,
            "CircleDescription": 1,
            "CircleDescriptor": 1,
            "ConicalBottomDescription": 1,
            "ConicalBottomDescriptor": 1,
            "FlatBottomDescription": 1,
            "FlatBottomDescriptor": 1,
            "GridDescription": 1,
            "GridDescriptor": 1,
            "LidDescription": 1,
            "LidDescriptor": 1,
            "PipetteTipBoxDescription": 1,
            "PipetteTipBoxDescriptor": 1,
        },
        "v1.36.0": {
            "PICK_UP_LABWARE": 2,
        },
    },
    renames={},
    replacements={},
)


def resolve_canonical_name(
    api_version: APIVersion,
    incoming_name: SchemaName,
    api_history_log: APIHistoryLog = TCodeAPIHistory,
) -> SchemaName:
    """Resolve the canonical name given an incoming name an an API version - accounts for command
    renames, deprecations, and removals.

    :param api_version: The API version to resolve the name for.
    :param incoming_name: The name to resolve.
    :param api_history_log: The API history log to use for resolution. Defaults to the TCodeAPIHistory.
        This parameter is primarily exposed for unittesting purposes.

    :returns: the resolved name corresponding to ``api_version``.
    """
    requested = Version(api_version)
    resolved_name = incoming_name

    # 1. Renames
    for v in sorted(api_history_log.renames, key=Version):
        if Version(v) > requested:
            break

        if resolved_name in api_history_log.renames[v]:
            resolved_name = api_history_log.renames[v][resolved_name]

    # 2. Deprecations
    for v in sorted(api_history_log.replacements, key=Version):
        if Version(v) > requested:
            break

        if resolved_name in api_history_log.replacements[v]:
            resolved_name = api_history_log.replacements[v][resolved_name]
            # TODO (connor): emit deprecation warning

    return resolved_name


def resolve_api_profile(
    api_version: APIVersion,
    api_history_log: APIHistoryLog = TCodeAPIHistory,
) -> dict[SchemaName, SchemaVersion]:
    """Resolve a schema-version profile for the given API version.

    :param api_version: The API version to resolve the profile for.
    :param api_history_log: The API history log to use for resolution. Defaults to the TCodeAPIHistory.
        This parameter is primarily exposed for unittesting purposes.

    :returns: a mapping of schema names to their respective versions for the given API version,
        taking into account all changes up to that version.
    """
    requested = Version(api_version)

    profile: dict[SchemaName, SchemaVersion] = {}

    # Create sorted list of version strings that modified the API
    versions_of_note = sorted(
        set(api_history_log.increments.keys())
        .union(set(api_history_log.renames.keys()))
        .union(set(api_history_log.replacements.keys())),
        key=Version,
    )
    for version_str in versions_of_note:

        # Check if we've got a modern enough version to return
        if Version(version_str) > requested:
            break

        # Handle increments, removals
        if version_str in api_history_log.increments:
            for schema_name, schema_version in api_history_log.increments[version_str].items():
                if schema_version is None:
                    profile.pop(schema_name)
                else:
                    profile[schema_name] = schema_version

        # Handle renames
        if version_str in api_history_log.renames:
            for old_schema_name, new_schema_name in api_history_log.renames[version_str].items():
                if new_schema_name in profile:
                    raise TargetSchemaExistsError(
                        f"Cannot rename '{old_schema_name}' to '{new_schema_name}' in profile '{profile}' because '{new_schema_name}' already exists in the profile."
                    )
                try:
                    profile[new_schema_name] = profile[old_schema_name]
                except KeyError:
                    raise TargetSchemaNotFoundError(
                        f"'{old_schema_name}' not found in profile '{profile}'"
                    )
                profile.pop(old_schema_name)

        # Handle replacements
        if version_str in api_history_log.replacements:
            for old_schema_name in api_history_log.replacements[version_str]:
                profile.pop(old_schema_name)

    return profile


# def load_command(raw: dict, api_version: str) -> object:
#     try:
#         incoming_name = raw["type"]
#     except KeyError as err:
#         raise InvalidSchemaError(
#             msg="Unable to find expected key 'type' in command schema",
#             bad_schema=raw,
#         ) from err
#
#     canonical_name = resolve_canonical_name(api_version, incoming_name)
#     profile = resolve_api_profile(api_version)
#
#     try:
#         schema_version = profile[canonical_name]
#     except KeyError:
#         raise UnsupportedModelError(canonical_name, api_version)
#
#     return load_model(
#         model_name=canonical_name,
#         schema_version=schema_version,
#         raw=raw,
#     )
