from ...registry import Migrator, RawData


def migrate_v1_to_v2(data: RawData) -> RawData:
    """Migrate a MOVE_TO_LOCATION command from schema version 1 to 2."""
    retval = {
        **data,
    }
    retval["schema_version"] = 2
    if "speed" not in retval:
        retval["speed"] = None  # Add the new field with a default value

    return retval


MIGRATORS: dict[int, Migrator] = {
    2: migrate_v1_to_v2,
}
