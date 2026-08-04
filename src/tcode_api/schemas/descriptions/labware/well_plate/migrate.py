from ....registry import Migrator, RawData
from ..lid.migrate import migrate_v3_to_v4 as migrate_lid_v3_to_v4


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


def migrate_v3_to_v4(data: RawData) -> RawData:
    """Migrate a WellPlateDescription or WellPlateDescriptor from schema version 3 to 4."""
    # v4 adds the required `pinchable` field. Well plates are pinched (not lifted) when picked up
    # (see robot.actions.move_plate.pick_up_plate), so pre-v4 well plates backfill as
    # pinchable=True. The nested lid (if present) is migrated via its own v3->v4 migrator so the
    # default-backfill logic for Lid lives in one place.
    retval = {
        **data,
    }
    retval["schema_version"] = 4
    retval.setdefault("pinchable", True)
    if retval.get("lid") is not None:
        retval["lid"] = migrate_lid_v3_to_v4(retval["lid"])
    return retval


MIGRATORS: dict[int, Migrator] = {
    2: migrate_v1_to_v2,
    3: migrate_v2_to_v3,
    4: migrate_v3_to_v4,
}
