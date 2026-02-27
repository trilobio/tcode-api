from typing import Literal

from pydantic import Field

from tcode_api.types import Matrix

from ..base import BaseLocation


class LocationRelativeToLabwareV1(BaseLocation):
    """Location specified by relative to a labware's..base node.

    This location type is designed to define points on continuous-surface labware
        (ex. agar plates.)
    """

    type: Literal["LocationRelativeToLabware"] = "LocationRelativeToLabware"
    schema_version: Literal[1] = 1

    labware_id: str = Field(
        description=(
            "TCode ID of the labware to target, "
            "assigned previously by the :class:``ADD_LABWARE`` command."
        ),
    )
    matrix: Matrix = Field(
        description=(
            "4x4 transformation matrix represented as a list of 16 floats in row-major order. "
            "The transform is applied relative to the labware's root node."
        ),
    )
