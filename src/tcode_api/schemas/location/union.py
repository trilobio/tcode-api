"""TCode location union - primarily used for typing."""

from typing import Annotated

from pydantic import Field

from .location_as_labware_holder.latest import (
    LocationAsLabwareHolder,
)
from .location_as_labware_index.latest import (
    LocationAsLabwareIndex,
)
from .location_as_node_id.latest import LocationAsNodeId
from .location_relative_to_current_position.latest import (
    LocationRelativeToCurrentPosition,
)
from .location_relative_to_labware.latest import (
    LocationRelativeToLabware,
)
from .location_relative_to_robot.latest import (
    LocationRelativeToRobot,
)
from .location_relative_to_world.latest import (
    LocationRelativeToWorld,
)

Location = Annotated[
    LocationAsLabwareIndex
    | LocationAsNodeId
    | LocationRelativeToCurrentPosition
    | LocationRelativeToLabware
    | LocationAsLabwareHolder
    | LocationRelativeToRobot
    | LocationRelativeToWorld,
    Field(
        discriminator="type", description="Union type of all valid TCode Location specifications."
    ),
]
