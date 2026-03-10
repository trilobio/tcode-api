from ...registry import migration_registry, schema_registry
from .latest import DELETE_LABWARE
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "DELETE_LABWARE",
        schema_version,
        migrator,
    )

schema_registry.register("DELETE_LABWARE", DELETE_LABWARE)
