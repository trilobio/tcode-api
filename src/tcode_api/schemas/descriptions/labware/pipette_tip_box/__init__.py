from pydantic import ValidationError

from ....registry import RawData, migration_registry, schema_registry
from .latest import PipetteTipBoxDescription, PipetteTipBoxDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "PipetteTipBox",
        schema_version,
        migrator,
    )


def _build_pipette_tip_box(data: RawData) -> PipetteTipBoxDescription | PipetteTipBoxDescriptor:
    """Build a PipetteTipBoxDescription, unless the data is missing fields, in which case build a PipetteTipBoxDescriptor."""
    try:
        return PipetteTipBoxDescription.model_validate(data)
    except ValidationError:
        return PipetteTipBoxDescriptor.model_validate(data)


schema_registry.register("PipetteTipBox", _build_pipette_tip_box)
