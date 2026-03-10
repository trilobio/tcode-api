from ...registry import migration_registry, schema_registry
from .latest import MOVE_GRIPPER
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "MOVE_GRIPPER",
        schema_version,
        migrator,
    )

schema_registry.register("MOVE_GRIPPER", MOVE_GRIPPER)
