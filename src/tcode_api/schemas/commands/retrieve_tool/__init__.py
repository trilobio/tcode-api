from ...registry import migration_registry, schema_registry
from .latest import RETRIEVE_TOOL
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "RETRIEVE_TOOL",
        schema_version,
        migrator,
    )

schema_registry.register("RETRIEVE_TOOL", RETRIEVE_TOOL)
