from pydantic import ValidationError

from ...registry import RawData, migration_registry, schema_registry
from .latest import CircleDescription, CircleDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "Circle",
        schema_version,
        migrator,
    )


def _build_circle(data: RawData) -> CircleDescription | CircleDescriptor:
    """Build a CircleDescription, unless the data is missing fields, in which case build a CircleDescriptor."""
    try:
        return CircleDescription.model_validate(data)
    except ValidationError:
        return CircleDescriptor.model_validate(data)


schema_registry.register("Circle", _build_circle)
