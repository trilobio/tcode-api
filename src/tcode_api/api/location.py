"""Data structures for defining locations in 3D space through TCode."""

from typing import Annotated, Literal

from pydantic import Field

from tcode_api.api.core import _ConfiguredBaseModel
from tcode_api.types import Matrix


class _Location(_ConfiguredBaseModel):
    """Base schema shared by all locations in the Location discriminated union."""

    type: str


class LocationRelativeToCurrentPosition(_Location):
    """Location specified by a transformation matrix relative to position of the robot's current control node."""

    type: Literal["LocationRelativeToCurrentPosition"] = "LocationRelativeToCurrentPosition"
    matrix: Matrix  # 4x4 transformation matrix


class LocationAsLabwareHolder(_Location):
    """Location specified by a labware holder's name."""

    type: Literal["LocationAsLabwareHolder"] = "LocationAsLabwareHolder"
    robot_id: str
    labware_holder_name: str


class LocationAsLabwareIndex(_Location):
    """Location specified by a tuple of labware id and labware location index."""

    type: Literal["LocationAsLabwareIndex"] = "LocationAsLabwareIndex"
    labware_id: str
    location_index: int
    well_part: str  # WellPartType


class LocationAsNodeId(_Location):
    """Location specified by a node ID in the fleet's transform tree."""

    type: Literal["LocationAsNodeId"] = "LocationAsNodeId"
    node_id: str


class LocationRelativeToLabware(_Location):
    """Location specified by a transformation matrix relative to a labware's base node."""

    type: Literal["LocationRelativeToLabware"] = "LocationRelativeToLabware"
    labware_id: str
    matrix: Matrix  # 4x4 transformation matrix


class LocationRelativeToWorld(_Location):
    """Location specified by a transformation matrix relative to the fleet's root node."""

    type: Literal["LocationRelativeToWorld"] = "LocationRelativeToWorld"
    matrix: Matrix  # 4x4 transformation matrix


Location = Annotated[
    LocationAsLabwareIndex
    | LocationAsNodeId
    | LocationRelativeToCurrentPosition
    | LocationRelativeToLabware
    | LocationRelativeToWorld,
    Field(discriminator="type"),
]
