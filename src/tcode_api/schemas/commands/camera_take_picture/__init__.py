from ...registry import migration_registry, schema_registry
from .latest import CAMERA_TAKE_PICTURE
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "CAMERA_TAKE_PICTURE",
        schema_version,
        migrator,
    )

schema_registry.register("CAMERA_TAKE_PICTURE", CAMERA_TAKE_PICTURE)
