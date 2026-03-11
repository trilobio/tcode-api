from typing import Callable

from ....registry import RawData


def migrate_v1_to_v2(data: RawData) -> RawData:
    """Migrate a WellPlateDescription or WellPlateDescriptor from schema version 1 to 2."""
    # No attribute changes — bump top-level schema_version and nested lid schema_version.
    retval = {
        **data,
    }
    retval["schema_version"] = 2
    if retval.get("lid") is not None:
        retval["lid"] = {**retval["lid"], "schema_version": 2}
    return retval


def migrate_v2_to_v3(data: RawData) -> RawData:
    """Migrate a WellPlateDescription or WellPlateDescriptor from schema version 2 to 3."""
    # No attribute changes — bump top-level schema_version and nested lid schema_version.
    retval = {
        **data,
    }
    retval["schema_version"] = 3
    if retval.get("lid") is not None:
        retval["lid"] = {**retval["lid"], "schema_version": 3}
    return retval


MIGRATORS: dict[int, Callable] = {
    2: migrate_v1_to_v2,
    3: migrate_v2_to_v3,
}
