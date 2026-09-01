from typing import Literal

from pydantic import Field

from ...common.value_with_units import ValueWithUnits
from ...location.location_as_labware_index.v1 import LocationAsLabwareIndex
from ...location.location_relative_to_labware.v1 import LocationRelativeToLabware
from ..base import BaseRobotSpecificTCodeCommand


class CALIBRATE_LABWARE_WELL_CENTER(BaseRobotSpecificTCodeCommand):
    """Tune the x/y center of a target labware's wells by probing a well's inner walls.

    The probe enters the well at the modeled center and probes horizontally in
    +x/-x/+y/-y until it contacts each wall; the midpoint of each opposing
    contact pair is taken as the well's true center.
    """

    type: Literal["CALIBRATE_LABWARE_WELL_CENTER"] = "CALIBRATE_LABWARE_WELL_CENTER"
    schema_version: Literal[1] = 1

    location: LocationAsLabwareIndex | LocationRelativeToLabware = Field(
        description=("Location specifying which labware and which well to probe.")
    )

    persistent: bool = Field(
        description="Whether calibration should persist beyond the current session."
    )

    modify_all_wells: bool = Field(
        default=True,
        description=("If true, modify the centers of all wells; otherwise only the probed well."),
    )

    max_probe_distance: ValueWithUnits | None = Field(
        default=None,
        description=(
            "Maximum horizontal travel from the modeled center commanded for each wall "
            "probe; must exceed the well's inner half-width at the probing height. "
            "Defaults to 20 mm; expects length units."
        ),
    )

    probe_height_above_bottom: ValueWithUnits | None = Field(
        default=None,
        description=(
            "Height above the well bottom at which the walls are probed. "
            "Defaults to 2 mm; expects length units."
        ),
    )
