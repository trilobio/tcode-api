from typing import Literal

from pydantic import Field

from ...location.location_as_labware_index.v1 import LocationAsLabwareIndexV1
from ...location.location_relative_to_labware.v1 import LocationRelativeToLabwareV1
from ..base import BaseRobotSpecificTCodeCommand


class CALIBRATE_LABWARE_HEIGHT_V1(BaseRobotSpecificTCodeCommand):
    """Tune the height of a target labware by probing."""

    type: Literal["CALIBRATE_LABWARE_HEIGHT"] = "CALIBRATE_LABWARE_HEIGHT"
    schema_version: Literal[1] = 1

    location: LocationAsLabwareIndexV1 | LocationRelativeToLabwareV1 = Field(
        description=("Location specifying which labware and where on the labware to probe.")
    )

    persistent: bool = Field(
        description=(
            "When true, all labware of the same type and brand will be modified. "
            "Otherwise, only the current in-place transform is applied."
        )
    )
