from typing import Callable

from ....registry import RawData
from .v2 import migrate_v1_to_v2


def migrate_v2_to_v3(data: RawData) -> RawData:
    """Migrate a PipetteTipBoxDescription or PipetteTipBoxDescriptor from schema version 2 to 3."""
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
