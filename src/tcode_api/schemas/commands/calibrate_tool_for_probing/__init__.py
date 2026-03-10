from ...registry import migration_registry, schema_registry
from .latest import CALIBRATE_TOOL_FOR_PROBING
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "CALIBRATE_TOOL_FOR_PROBING",
        schema_version,
        migrator,
    )

schema_registry.register("CALIBRATE_TOOL_FOR_PROBING", CALIBRATE_TOOL_FOR_PROBING)
