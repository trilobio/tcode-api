from ...registry import Migrator, RawData


def migrate_v1_to_v2(data: RawData) -> RawData:
    """Migrate an DISPENSE command from schema version 1 to 2."""
    retval = {
        **data,
    }
    retval["schema_version"] = 2
    retval.setdefault("relative_movement_offset", None)
    return retval


MIGRATORS: dict[int, Migrator] = {
    2: migrate_v1_to_v2,
}
