from typing import Literal

from pydantic import Field

from tcode_api.types import Matrix

from ..base.location.v1 import BaseLocationV1


class LocationRelativeToWorld(BaseLocationV1):
    """Location specified relative to the fleet's root node."""

    type: Literal["LocationRelativeToWorld"] = "LocationRelativeToWorld"
    schema_version: Literal[1] = 1

    matrix: Matrix = Field(
        description=(
            "4x4 transformation matrix represented as a list of 16 floats in row-major order. "
            "The transform is applied relative to the fleet's root node."
        ),
    )
