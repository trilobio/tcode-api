from ...registry import migration_registry, schema_registry
from .latest import DISCARD_PIPETTE_TIP_GROUP
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "DISCARD_PIPETTE_TIP_GROUP",
        schema_version,
        migrator,
    )

schema_registry.register("DISCARD_PIPETTE_TIP_GROUP", DISCARD_PIPETTE_TIP_GROUP)
