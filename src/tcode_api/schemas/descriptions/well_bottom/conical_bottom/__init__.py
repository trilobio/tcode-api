from ....registry import (
    RawData,
    build_description_or_descriptor,
    migration_registry,
    schema_registry,
)
from .latest import ConicalBottomDescription, ConicalBottomDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "Conical",
        schema_version,
        migrator,
    )


def _build_conical(data: RawData) -> ConicalBottomDescription | ConicalBottomDescriptor:
    """Build a ConicalBottomDescription, unless the data is missing fields, in which case build a ConicalBottomDescriptor."""
    return build_description_or_descriptor(ConicalBottomDescription, ConicalBottomDescriptor, data)


schema_registry.register("Conical", _build_conical)
