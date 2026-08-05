from ...registry import (
    RawData,
    build_description_or_descriptor,
    migration_registry,
    schema_registry,
)
from .latest import CircleDescription, CircleDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "Circle",
        schema_version,
        migrator,
    )


def _build_circle(data: RawData) -> CircleDescription | CircleDescriptor:
    """Build a CircleDescription, unless the data is missing fields, in which case build a CircleDescriptor."""
    return build_description_or_descriptor(CircleDescription, CircleDescriptor, data)


schema_registry.register("Circle", _build_circle)
