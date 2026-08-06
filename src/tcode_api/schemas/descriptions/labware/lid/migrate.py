from ....registry import Migrator, RawData


def migrate_v1_to_v2(data: RawData) -> RawData:
    """Migrate a LidDescription or LidDescriptor from schema version 1 to 2."""
    # No changes between v1 and v2 other than semver, so we can just return the data unchanged.
    retval = {
        **data,
    }
    retval["schema_version"] = 2
    return retval


def migrate_v2_to_v3(data: RawData) -> RawData:
    """Migrate a LidDescription or LidDescriptor from schema version 2 to 3."""
    # No changes between v2 and v3 other than semver, so we can just return the data unchanged.
    retval = {
        **data,
    }
    retval["schema_version"] = 3
    return retval


# Prior to tcode-api v1.42.0, `aceta` set a default pinch offset of 2mm in z...
# https://github.com/trilobio/aceta/blob/772760d53f35f5574e95f77dd40ed03ffcb6f9ba/tcode/tcode/resolver/create_labware.py#L259
_DEFAULT_PINCH_OFFSET_TRANSFORM: list[list[float]] = [
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.002],
    [0.0, 0.0, 0.0, 1.0],
]


def migrate_v3_to_v4(data: RawData) -> RawData:
    """Migrate a LidDescription or LidDescriptor from schema version 3 to 4."""
    # v4 adds the required `pinchable` field. Lids are pinched (not lifted) when picked up (see
    # robot.actions.move_plate.pick_up_plate), so pre-v4 lids backfill as pinchable=True.
    retval = {
        **data,
    }
    retval["schema_version"] = 4
    retval.setdefault("pinchable", True)
    retval.setdefault("pinch_offset_transform", _DEFAULT_PINCH_OFFSET_TRANSFORM)
    return retval


MIGRATORS: dict[int, Migrator] = {
    2: migrate_v1_to_v2,
    3: migrate_v2_to_v3,
    4: migrate_v3_to_v4,
}
