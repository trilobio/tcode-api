from ...registry import migration_registry, schema_registry
from .latest import ADD_ROBOT
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "ADD_ROBOT",
        schema_version,
        migrator,
    )

schema_registry.register("ADD_ROBOT", ADD_ROBOT)
