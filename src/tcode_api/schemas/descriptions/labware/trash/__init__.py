from pydantic import ValidationError

from ....registry import RawData, migration_registry, schema_registry
from .latest import TrashDescription, TrashDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "Trash",
        schema_version,
        migrator,
    )


def _build_trash(data: RawData) -> TrashDescription | TrashDescriptor:
    """Build a TrashDescription, unless the data is missing fields, in which case build a TrashDescriptor."""
    try:
        return TrashDescription.model_validate(data)
    except ValidationError:
        return TrashDescriptor.model_validate(data)


schema_registry.register("Trash", _build_trash)
