from pydantic import ValidationError

from ...registry import RawData, migration_registry, schema_registry
from .latest import WellDescription, WellDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "Well",
        schema_version,
        migrator,
    )


def _build_well(data: RawData) -> WellDescription | WellDescriptor:
    """Build a WellDescription, unless the data is missing fields, in which case build a WellDescriptor."""
    try:
        return WellDescription.model_validate(data)
    except ValidationError:
        return WellDescriptor.model_validate(data)


schema_registry.register("Well", _build_well)
