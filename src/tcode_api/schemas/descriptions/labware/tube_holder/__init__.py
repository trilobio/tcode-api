from ....registry import (
    RawData,
    build_description_or_descriptor,
    migration_registry,
    schema_registry,
)
from .latest import TubeHolderDescription, TubeHolderDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "TubeHolder",
        schema_version,
        migrator,
    )


def _build_tube_holder(data: RawData) -> TubeHolderDescription | TubeHolderDescriptor:
    """Build a TubeHolderDescription, unless the data is missing fields, in which case build a TubeHolderDescriptor."""
    return build_description_or_descriptor(TubeHolderDescription, TubeHolderDescriptor, data)


schema_registry.register("TubeHolder", _build_tube_holder)
