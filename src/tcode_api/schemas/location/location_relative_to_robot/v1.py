from typing import Literal

from pydantic import Field

from tcode_api.types import Matrix

from ..base import BaseLocation


class LocationRelativeToRobotV1(BaseLocation):
    """Location relative to the robot's root node."""

    type: Literal["LocationRelativeToRobot"] = "LocationRelativeToRobot"
    schema_version: Literal[1] = 1

    robot_id: str = Field(
        description=(
            "TCode ID of the robot to target, "
            "assigned previously by the :class:``ADD_ROBOT`` command."
        ),
    )
    matrix: Matrix = Field(
        description=(
            "4x4 transformation matrix represented as a list of 16 floats in row-major order. "
            "The transform is applied relative to the robot's root node."
        ),
    )
