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


# Prior to tcode-api v1.42.0, `aceta` set a default pinch offset of 10mm in z...
# https://github.com/trilobio/aceta/blob/772760d53f35f5574e95f77dd40ed03ffcb6f9ba/tcode/tcode/resolver/create_labware.py#L94
_DEFAULT_PINCH_OFFSET_TRANSFORM: list[list[float]] = [
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.010],
    [0.0, 0.0, 0.0, 1.0],
]


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
    retval.setdefault("pinch_offset_transform", _DEFAULT_PINCH_OFFSET_TRANSFORM)
    if retval.get("lid") is not None:
        retval["lid"] = migrate_lid_v3_to_v4(retval["lid"])
    return retval


MIGRATORS: dict[int, Migrator] = {
    2: migrate_v1_to_v2,
    3: migrate_v2_to_v3,
    4: migrate_v3_to_v4,
}
