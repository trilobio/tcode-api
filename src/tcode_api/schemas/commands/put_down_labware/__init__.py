from ...registry import migration_registry, schema_registry
from .latest import PUT_DOWN_LABWARE
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "PUT_DOWN_LABWARE",
        schema_version,
        migrator,
    )

schema_registry.register("PUT_DOWN_LABWARE", PUT_DOWN_LABWARE)
