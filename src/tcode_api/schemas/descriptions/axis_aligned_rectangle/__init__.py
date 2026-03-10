from pydantic import ValidationError

from ...registry import RawData, migration_registry, schema_registry
from .latest import AxisAlignedRectangleDescription, AxisAlignedRectangleDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "AxisAlignedRectangle",
        schema_version,
        migrator,
    )


def _build_axis_aligned_rectangle(
    data: RawData,
) -> AxisAlignedRectangleDescription | AxisAlignedRectangleDescriptor:
    """Build an AxisAlignedRectangleDescription, unless the data is missing fields, in which case build an AxisAlignedRectangleDescriptor."""
    try:
        return AxisAlignedRectangleDescription.model_validate(data)
    except ValidationError:
        return AxisAlignedRectangleDescriptor.model_validate(data)


schema_registry.register("AxisAlignedRectangle", _build_axis_aligned_rectangle)
