from pydantic import ValidationError

from ....registry import RawData, migration_registry, schema_registry
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
    try:
        return RoundBottomDescription.model_validate(data)
    except ValidationError:
        return RoundBottomDescriptor.model_validate(data)


schema_registry.register("Round", _build_round)
