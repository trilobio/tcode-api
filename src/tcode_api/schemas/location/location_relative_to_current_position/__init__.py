from ...registry import migration_registry, schema_registry
from .latest import LocationRelativeToCurrentPosition
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "LocationRelativeToCurrentPosition",
        schema_version,
        migrator,
    )

schema_registry.register("LocationRelativeToCurrentPosition", LocationRelativeToCurrentPosition)
