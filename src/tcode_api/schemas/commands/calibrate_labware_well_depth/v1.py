from typing import Literal

from pydantic import Field

from ...location.location_as_labware_index.v1 import LocationAsLabwareIndexV1
from ...location.location_relative_to_labware.v1 import LocationRelativeToLabwareV1
from ..base import BaseRobotSpecificTCodeCommand


class CALIBRATE_LABWARE_WELL_DEPTH_V1(BaseRobotSpecificTCodeCommand):
    """Tune the depth of a target labware's well by probing."""

    type: Literal["CALIBRATE_LABWARE_WELL_DEPTH"] = "CALIBRATE_LABWARE_WELL_DEPTH"
    schema_version: Literal[1] = 1

    location: LocationAsLabwareIndexV1 | LocationRelativeToLabwareV1 = Field(
        description=("Location specifying which labware and where on the labware to probe.")
    )

    persistent: bool = Field(
        description="Whether calibration should persist beyond the current session."
    )

    modify_all_wells: bool = Field(
        default=True,
        description=("If true, modify the depths of all wells; otherwise only the probed well."),
    )
