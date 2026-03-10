from typing import Literal

from pydantic import Field

from tcode_api.types import Matrix

from ..base import BaseLocation


class LocationRelativeToCurrentPositionV1(BaseLocation):
    """Location specified by a transformation matrix relative to position of the robot's current control node."""

    type: Literal["LocationRelativeToCurrentPosition"] = "LocationRelativeToCurrentPosition"
    schema_version: Literal[1] = 1

    matrix: Matrix = Field(
        description=(
            "4x4 transformation matrix represented as a list of 16 floats in row-major order. "
            "The transform is applied relative to the robot's current control node position."
        ),
    )
