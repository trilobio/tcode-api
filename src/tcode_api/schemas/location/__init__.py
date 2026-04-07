"""TCode location schemas."""

# This module re-exports all location classes and the Location discriminated union from their
# versioned submodules. The __init__.py structure at each schemas submodule level is maintained
# explicitly to support Sphinx automodule autodoc generation for the tcode_api documentation.

from .location_as_labware_holder.latest import LocationAsLabwareHolder
from .location_as_labware_index.latest import LocationAsLabwareIndex
from .location_as_node_id.latest import LocationAsNodeId
from .location_relative_to_current_position.latest import (
    LocationRelativeToCurrentPosition,
)
from .location_relative_to_labware.latest import LocationRelativeToLabware
from .location_relative_to_robot.latest import LocationRelativeToRobot
from .location_relative_to_world.latest import LocationRelativeToWorld
from .union import Location

__all__ = [
    "Location",
    "LocationAsLabwareHolder",
    "LocationAsLabwareIndex",
    "LocationAsNodeId",
    "LocationRelativeToCurrentPosition",
    "LocationRelativeToLabware",
    "LocationRelativeToRobot",
    "LocationRelativeToWorld",
]
