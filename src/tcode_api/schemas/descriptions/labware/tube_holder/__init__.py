from pydantic import ValidationError

from ....registry import RawData, migration_registry, schema_registry
from .latest import TubeHolderDescription, TubeHolderDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "TubeHolder",
        schema_version,
        migrator,
    )


def _build_tube_holder(data: RawData) -> TubeHolderDescription | TubeHolderDescriptor:
    """Build a TubeHolderDescription, unless the data is missing fields, in which case build a TubeHolderDescriptor."""
    try:
        return TubeHolderDescription.model_validate(data)
    except ValidationError:
        return TubeHolderDescriptor.model_validate(data)


schema_registry.register("TubeHolder", _build_tube_holder)
