from ...registry import migration_registry, schema_registry
from .latest import CALIBRATE_LABWARE_HEIGHT
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "CALIBRATE_LABWARE_HEIGHT",
        schema_version,
        migrator,
    )

schema_registry.register("CALIBRATE_LABWARE_HEIGHT", CALIBRATE_LABWARE_HEIGHT)
