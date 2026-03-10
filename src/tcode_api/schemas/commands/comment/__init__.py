from ...registry import migration_registry, schema_registry
from .latest import COMMENT
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "COMMENT",
        schema_version,
        migrator,
    )

schema_registry.register("COMMENT", COMMENT)
