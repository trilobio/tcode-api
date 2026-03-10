from pydantic import ValidationError

from ...registry import RawData, migration_registry, schema_registry
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
    try:
        return TubeDescription.model_validate(data)
    except ValidationError:
        return TubeDescriptor.model_validate(data)


schema_registry.register("Tube", _build_tube)
