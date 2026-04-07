"""TCode pipette tip layout schema."""

# This module re-exports PipetteTipLayout from its versioned submodule.
# The __init__.py structure at each schemas submodule level is maintained explicitly
# to support Sphinx automodule autodoc generation for the tcode_api documentation.

from ..registry import migration_registry, schema_registry
from .latest import PipetteTipLayout
from .migrate import MIGRATORS

for schema_version, migrator in MIGRATORS.items():
    migration_registry.register_migrator(
        "PipetteTipLayout",
        schema_version,
        migrator,
    )

schema_registry.register("PipetteTipLayout", PipetteTipLayout)

__all__ = ["PipetteTipLayout"]
