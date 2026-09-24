from ...registry import (
    RawData,
    build_description_or_descriptor,
    migration_registry,
    schema_registry,
)
from .latest import TubeDescription, TubeDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "Tube",
        schema_version,
        migrator,
    )


def _build_tube(data: RawData) -> TubeDescription | TubeDescriptor:
    """Build a TubeDescription, unless the data is missing fields, in which case build a TubeDescriptor."""
    return build_description_or_descriptor(TubeDescription, TubeDescriptor, data)


schema_registry.register("Tube", _build_tube)
