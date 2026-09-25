from typing import Literal

from pydantic import Field

from ...location.location_as_labware_index.v1 import LocationAsLabwareIndex
from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class CALIBRATE_LABWARE_WELL_CENTER(BaseRobotSpecificTCodeCommandV1):
    """Tune the x/y center of a target labware's wells by probing a well's inner walls.

    The probe is assumed to already be inside the target well; this command moves in x/y
    only, at whatever height the probe currently holds. Positioning it (and choosing a
    height clear of the well bottom) is the caller's responsibility.

    Each axis is probed in both directions and the midpoint of the opposing contact pair
    is taken as the center along that axis. Axes are probed X -> Y -> X, re-centering the
    probing origin after each pass, so the final X pass discards the error picked up while
    still off-center in Y.
    """

    type: Literal["CALIBRATE_LABWARE_WELL_CENTER"] = "CALIBRATE_LABWARE_WELL_CENTER"
    schema_version: Literal[1] = 1

    location: LocationAsLabwareIndex = Field(
        description=(
            "Location specifying which labware and which well to probe. Only "
            "`LocationAsLabwareIndex` is accepted: re-centering is defined per well, and "
            "`LocationRelativeToLabware` carries no well index."
        )
    )

    persistent: bool = Field(
        description="Whether calibration should persist beyond the current session."
    )

    modify_all_wells: bool = Field(
        default=True,
        description=("If true, modify the centers of all wells; otherwise only the probed well."),
    )
