from ...registry import (
    RawData,
    build_description_or_descriptor,
    migration_registry,
    schema_registry,
)
from .latest import PipetteTipDescription, PipetteTipDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "PipetteTip",
        schema_version,
        migrator,
    )


def _build_pipette_tip(data: RawData) -> PipetteTipDescription | PipetteTipDescriptor:
    """Build a PipetteTipDescription, unless the data is missing fields, in which case build a PipetteTipDescriptor."""
    return build_description_or_descriptor(PipetteTipDescription, PipetteTipDescriptor, data)


schema_registry.register("PipetteTip", _build_pipette_tip)
