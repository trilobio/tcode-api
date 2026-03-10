from ....registry import migration_registry, schema_registry
from .latest import GripperDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "Gripper",
        schema_version,
        migrator,
    )

schema_registry.register("Gripper", GripperDescriptor)
