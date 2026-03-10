from pydantic import ValidationError

from ....registry import RawData, migration_registry, schema_registry
from .latest import FlatBottomDescription, FlatBottomDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "Flat",
        schema_version,
        migrator,
    )


def _build_flat(data: RawData) -> FlatBottomDescription | FlatBottomDescriptor:
    """Build a FlatBottomDescription, unless the data is missing fields, in which case build a FlatBottomDescriptor."""
    try:
        return FlatBottomDescription.model_validate(data)
    except ValidationError:
        return FlatBottomDescriptor.model_validate(data)


schema_registry.register("Flat", _build_flat)
