from typing import Callable

from ...registry import RawData


def migrate_v1_to_v2(data: RawData) -> RawData:
    """Migrate a CREATE_LABWARE command from schema version 1 to 2."""
    # No changes between v1 and v2 other than semver, so we can just return the data unchanged.
    retval = {
        **data,
    }
    retval["schema_version"] = 2
    return retval


def migrate_v2_to_v3(data: RawData) -> RawData:
    """Migrate a CREATE_LABWARE command from schema version 2 to 3."""
    # No changes between v2 and v3 other than semver, so we can just return the data unchanged.
    retval = {
        **data,
    }
    retval["schema_version"] = 3
    return retval


MIGRATORS: dict[int, Callable] = {
    2: migrate_v1_to_v2,
    3: migrate_v2_to_v3,
}
