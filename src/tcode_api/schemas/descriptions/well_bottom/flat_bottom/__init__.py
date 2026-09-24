from ....registry import (
    RawData,
    build_description_or_descriptor,
    migration_registry,
    schema_registry,
)
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
    return build_description_or_descriptor(FlatBottomDescription, FlatBottomDescriptor, data)


schema_registry.register("Flat", _build_flat)
