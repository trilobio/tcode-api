from ...registry import Migrator, RawData


def migrate_v1_to_v2(data: RawData) -> RawData:
    """Migrate a SEND_WEBHOOK command from schema version 1 to 2.

    v2 adds an optional ``robot_id``; absent in v1 payloads, it defaults to
    None (the engine rejects scheduling without one, with a clear error).
    """
    retval = {
        **data,
    }
    retval["schema_version"] = 2
    return retval


MIGRATORS: dict[int, Migrator] = {
    2: migrate_v1_to_v2,
}
