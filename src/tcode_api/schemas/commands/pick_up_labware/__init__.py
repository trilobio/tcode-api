from ...registry import migration_registry, schema_registry
from .latest import PICK_UP_LABWARE
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "PICK_UP_LABWARE",
        schema_version,
        migrator,
    )

schema_registry.register("PICK_UP_LABWARE", PICK_UP_LABWARE)
