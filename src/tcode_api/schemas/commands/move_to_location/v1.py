from typing import Literal

from pydantic import Field

from ....types import Matrix, identity_transform
from ...location.union import Location
from ..base import BaseRobotSpecificTCodeCommand


class MOVE_TO_LOCATION_V1(BaseRobotSpecificTCodeCommand):
    """Move the robot's control point to a specified location."""

    type: Literal["MOVE_TO_LOCATION"] = "MOVE_TO_LOCATION"
    schema_version: Literal[1] = 1

    location: Location = Field(description="Target location to move to.")

    location_offset: Matrix = Field(
        default_factory=identity_transform,
        description="Optional offset transform applied to the target location.",
    )

    flange: Location | None = Field(
        default=None,
        description="Optional non-default control point.",
    )

    flange_offset: Matrix = Field(
        default_factory=identity_transform,
        description="Optional offset applied to the flange location.",
    )

    # note: cast as int to make TypeScript stuff not break
    path_type: int | None = Field(
        default=None,
        description="Optional path type (:class:``PathType``).",
    )

    # note: cast as int to make TypeScript stuff not break
    trajectory_type: int | None = Field(
        default=None,
        description="Optional trajectory type (:class:``TrajectoryType``).",
    )
