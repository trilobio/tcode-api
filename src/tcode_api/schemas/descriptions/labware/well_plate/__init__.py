from pydantic import ValidationError

from ....registry import RawData, migration_registry, schema_registry
from .latest import WellPlateDescription, WellPlateDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "WellPlate",
        schema_version,
        migrator,
    )


def _build_well_plate(data: RawData) -> WellPlateDescription | WellPlateDescriptor:
    """Build a WellPlateDescription, unless the data is missing fields, in which case build a WellPlateDescriptor."""
    try:
        return WellPlateDescription.model_validate(data)
    except ValidationError:
        return WellPlateDescriptor.model_validate(data)


schema_registry.register("WellPlate", _build_well_plate)
