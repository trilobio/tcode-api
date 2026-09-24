from ....registry import (
    RawData,
    build_description_or_descriptor,
    migration_registry,
    schema_registry,
)
from .latest import RoundBottomDescription, RoundBottomDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "Round",
        schema_version,
        migrator,
    )


def _build_round(data: RawData) -> RoundBottomDescription | RoundBottomDescriptor:
    """Build a RoundBottomDescription, unless the data is missing fields, in which case build a RoundBottomDescriptor."""
    return build_description_or_descriptor(RoundBottomDescription, RoundBottomDescriptor, data)


schema_registry.register("Round", _build_round)
