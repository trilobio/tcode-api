from ...registry import migration_registry, schema_registry
from .latest import CREATE_LABWARE
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "CREATE_LABWARE",
        schema_version,
        migrator,
    )

schema_registry.register("CREATE_LABWARE", CREATE_LABWARE)
