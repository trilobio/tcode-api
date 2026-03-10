from pydantic import ValidationError

from ....registry import RawData, migration_registry, schema_registry
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
    try:
        return VBottomDescription.model_validate(data)
    except ValidationError:
        return VBottomDescriptor.model_validate(data)


schema_registry.register("V-Shape", _build_v_shape)
