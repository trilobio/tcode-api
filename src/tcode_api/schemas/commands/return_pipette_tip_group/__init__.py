from ...registry import migration_registry, schema_registry
from .latest import RETURN_PIPETTE_TIP_GROUP
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "RETURN_PIPETTE_TIP_GROUP",
        schema_version,
        migrator,
    )

schema_registry.register("RETURN_PIPETTE_TIP_GROUP", RETURN_PIPETTE_TIP_GROUP)
