from ...registry import Migrator, RawData


def migrate_v1_to_v2(data: RawData) -> RawData:
    """Migrate an ADD_PIPETTE_TIP_GROUP command from schema version 1 to 2.

    v2 introduces a required ``robot_id`` field (the pipette tip group is now scoped to a
    specific robot). v1 payloads do not carry a ``robot_id``; rather than fabricate one
    silently, this migrator raises so the caller can decide which robot owns the group.
    """
    if "robot_id" not in data:
        raise ValueError(
            "Cannot migrate ADD_PIPETTE_TIP_GROUP v1 to v2 automatically: v2 requires a 'robot_id'."
        )
    retval = {**data}
    retval["schema_version"] = 2
    return retval


def migrate_v2_to_v3(data: RawData) -> RawData:
    """Migrate an ADD_PIPETTE_TIP_GROUP command from schema version 2 to 3.

    v3 introduces new optional `pipette_tip_locations` field which is set to None during migration.
    """
    retval = {**data}
    retval["schema_version"] = 3
    if "pipette_tip_locations" not in retval:
        retval["pipette_tip_locations"] = None

    return retval


MIGRATORS: dict[int, Migrator] = {
    2: migrate_v1_to_v2,
    3: migrate_v2_to_v3,
}
