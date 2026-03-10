from ...registry import migration_registry, schema_registry
from .latest import SWAP_TO_TOOL
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "SWAP_TO_TOOL",
        schema_version,
        migrator,
    )

schema_registry.register("SWAP_TO_TOOL", SWAP_TO_TOOL)
