from ...registry import migration_registry, schema_registry
from .latest import REMOVE_LABWARE_LID
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "REMOVE_LABWARE_LID",
        schema_version,
        migrator,
    )

schema_registry.register("REMOVE_LABWARE_LID", REMOVE_LABWARE_LID)
