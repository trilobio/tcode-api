from typing import Callable

from ...registry import RawData


def migrate_v1_to_v2(data: RawData) -> RawData:
    """Migrate a PAUSE command from schema version 1 to 2.

    v2 introduces a required ``robot_id`` field (PAUSE is now a robot-specific command).
    v1 payloads do not carry a ``robot_id``; rather than fabricate one silently, this migrator
    raises so the caller can decide which robot the legacy command should target.
    """
    if "robot_id" not in data:
        raise ValueError(
            "Cannot migrate PAUSE v1 to v2 automatically: v2 requires a 'robot_id'. "
            "Schedule a separate PAUSE per robot, optionally grouped via 'sync_group'."
        )
    retval = {**data}
    retval["schema_version"] = 2
    return retval


MIGRATORS: dict[int, Callable] = {
    2: migrate_v1_to_v2,
}
