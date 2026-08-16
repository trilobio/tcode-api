from ...registry import migration_registry, schema_registry
from .latest import CAMERA_STOP_RECORDING
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "CAMERA_STOP_RECORDING",
        schema_version,
        migrator,
    )

schema_registry.register("CAMERA_STOP_RECORDING", CAMERA_STOP_RECORDING)
