from pydantic import ValidationError

from ....registry import RawData, migration_registry, schema_registry
from .latest import LidDescription, LidDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "Lid",
        schema_version,
        migrator,
    )


def _build_lid(data: RawData) -> LidDescription | LidDescriptor:
    """Build a LidDescription, unless the data is missing fields, in which case build a LidDescriptor."""
    try:
        return LidDescription.model_validate(data)
    except ValidationError:
        return LidDescriptor.model_validate(data)


schema_registry.register("Lid", _build_lid)
