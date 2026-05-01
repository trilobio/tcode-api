from typing import Callable

from ...registry import RawData


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


MIGRATORS: dict[int, Callable] = {
    2: migrate_v1_to_v2,
}
