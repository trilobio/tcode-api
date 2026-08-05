from ....registry import (
    RawData,
    build_description_or_descriptor,
    migration_registry,
    schema_registry,
)
from .latest import VBottomDescription, VBottomDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "V-Shape",
        schema_version,
        migrator,
    )


def _build_v_shape(data: RawData) -> VBottomDescription | VBottomDescriptor:
    """Build a VBottomDescription, unless the data is missing fields, in which case build a VBottomDescriptor."""
    return build_description_or_descriptor(VBottomDescription, VBottomDescriptor, data)


schema_registry.register("V-Shape", _build_v_shape)
