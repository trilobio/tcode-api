from ...registry import migration_registry, schema_registry
from .latest import MOVE_TO_LOCATION
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "MOVE_TO_LOCATION",
        schema_version,
        migrator,
    )

schema_registry.register("MOVE_TO_LOCATION", MOVE_TO_LOCATION)
