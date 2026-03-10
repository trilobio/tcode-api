from ...registry import migration_registry, schema_registry
from .latest import SEND_WEBHOOK
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "SEND_WEBHOOK",
        schema_version,
        migrator,
    )

schema_registry.register("SEND_WEBHOOK", SEND_WEBHOOK)
