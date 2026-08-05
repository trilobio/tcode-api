from ....registry import Migrator, RawData


def migrate_v1_to_v2(data: RawData) -> RawData:
    """Migrate a TrashDescription or TrashDescriptor from schema version 1 to 2."""
    # No changes between v1 and v2 other than semver, so we can just return the data unchanged.
    retval = {
        **data,
    }
    retval["schema_version"] = 2
    return retval


def migrate_v2_to_v3(data: RawData) -> RawData:
    """Migrate a TrashDescription or TrashDescriptor from schema version 2 to 3."""
    # No changes between v2 and v3 other than semver, so we can just return the data unchanged.
    retval = {
        **data,
    }
    retval["schema_version"] = 3
    return retval


def migrate_v3_to_v4(data: RawData) -> RawData:
    """Migrate a TrashDescription or TrashDescriptor from schema version 3 to 4."""
    # v4 adds the required `pinchable` field. Trash bins are lifted (not pinched) when picked up
    # (see tcode.resolver.create_labware.build_trash_from_description's pinch_transform=None), so
    # pre-v4 trash bins backfill as pinchable=False.
    retval = {
        **data,
    }
    retval["schema_version"] = 4
    retval.setdefault("pinchable", False)
    retval.setdefault("pinch_offset_transform", None)
    return retval


MIGRATORS: dict[int, Migrator] = {
    2: migrate_v1_to_v2,
    3: migrate_v2_to_v3,
    4: migrate_v3_to_v4,
}
