from ...registry import (
    RawData,
    build_description_or_descriptor,
    migration_registry,
    schema_registry,
)
from .latest import GridDescription, GridDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "Grid",
        schema_version,
        migrator,
    )


def _build_grid(data: RawData) -> GridDescription | GridDescriptor:
    """Build a GridDescription, unless the data is missing fields, in which case build a GridDescriptor."""
    return build_description_or_descriptor(GridDescription, GridDescriptor, data)


schema_registry.register("Grid", _build_grid)
