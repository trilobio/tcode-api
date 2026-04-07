"""TCode script schemas: top-level script and metadata."""

# This module re-exports TCodeScript and Metadata from their versioned submodules.
# The __init__.py structure at each schemas submodule level is maintained explicitly
# to support Sphinx automodule autodoc generation for the tcode_api documentation.

from .metadata import Metadata
from .tcode_script import TCodeScript

__all__ = [
    "Metadata",
    "TCodeScript",
]
