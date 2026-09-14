from ...registry import (
    RawData,
    build_description_or_descriptor,
    migration_registry,
    schema_registry,
)
from .latest import LiddabilityDescription, LiddabilityDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "Liddability",
        schema_version,
        migrator,
    )


def _build_liddability(data: RawData) -> LiddabilityDescription | LiddabilityDescriptor:
    """Build a LiddabilityDescription, unless the data is missing fields, in which case build a LiddabilityDescriptor."""
    return build_description_or_descriptor(LiddabilityDescription, LiddabilityDescriptor, data)


schema_registry.register("Liddability", _build_liddability)
