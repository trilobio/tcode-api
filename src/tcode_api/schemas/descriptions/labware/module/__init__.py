from pydantic import ValidationError

from ....registry import RawData, migration_registry, schema_registry
from .latest import ModuleDescription, ModuleDescriptor
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "Module",
        schema_version,
        migrator,
    )


def _build_module(data: RawData) -> ModuleDescription | ModuleDescriptor:
    """Build a ModuleDescription, unless the data is missing fields, in which case build a ModuleDescriptor."""
    try:
        return ModuleDescription.model_validate(data)
    except ValidationError:
        return ModuleDescriptor.model_validate(data)


schema_registry.register("Module", _build_module)
