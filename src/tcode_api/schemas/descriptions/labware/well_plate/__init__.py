from ....registry import (
    RawData,
    build_description_or_descriptor,
    migration_registry,
    schema_registry,
)
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
    return build_description_or_descriptor(WellPlateDescription, WellPlateDescriptor, data)


schema_registry.register("WellPlate", _build_well_plate)
