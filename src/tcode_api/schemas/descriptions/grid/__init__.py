from pydantic import ValidationError

from ...registry import RawData, migration_registry, schema_registry
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
    try:
        return GridDescription.model_validate(data)
    except ValidationError:
        return GridDescriptor.model_validate(data)


schema_registry.register("Grid", _build_grid)
