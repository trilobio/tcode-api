from ....types import identity_transform
from ...common.enums import GraspType
from ...registry import Migrator, RawData


def migrate_v1_to_v2(data: RawData) -> RawData:
    """Migrate a REPLACE_LABWARE_LID from schema version 1 to 2."""
    retval = {
        **data,
    }
    retval["schema_version"] = 2
    if not "grasp_type" in retval:
        retval["grasp_type"] = GraspType.PINCH.value
    if not "offset_transform" in retval:
        retval["offset_transform"] = identity_transform()
    return retval


MIGRATORS: dict[int, Migrator] = {
    2: migrate_v1_to_v2,
}
