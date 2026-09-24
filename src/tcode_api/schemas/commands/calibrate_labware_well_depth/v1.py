from typing import Literal

from pydantic import Field

from ...location.location_as_labware_index.v1 import LocationAsLabwareIndex
from ...location.location_relative_to_labware.v1 import LocationRelativeToLabware
from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class CALIBRATE_LABWARE_WELL_DEPTH(BaseRobotSpecificTCodeCommandV1):
    """Tune the depth of a target labware's well by probing."""

    type: Literal["CALIBRATE_LABWARE_WELL_DEPTH"] = "CALIBRATE_LABWARE_WELL_DEPTH"
    schema_version: Literal[1] = 1

    location: LocationAsLabwareIndex | LocationRelativeToLabware = Field(
        description=("Location specifying which labware and where on the labware to probe.")
    )

    persistent: bool = Field(
        description="Whether calibration should persist beyond the current session."
    )

    modify_all_wells: bool = Field(
        default=True,
        description=("If true, modify the depths of all wells; otherwise only the probed well."),
    )
