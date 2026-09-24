from ...registry import (
    RawData,
    build_description_or_descriptor,
    migration_registry,
    schema_registry,
)
from .latest import WellDescription, WellDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "Well",
        schema_version,
        migrator,
    )


def _build_well(data: RawData) -> WellDescription | WellDescriptor:
    """Build a WellDescription, unless the data is missing fields, in which case build a WellDescriptor."""
    return build_description_or_descriptor(WellDescription, WellDescriptor, data)


schema_registry.register("Well", _build_well)
