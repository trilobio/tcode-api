"""WellPlateDescriptor & WellPlateDescription v5

- Increment `lid` attribute to v5.
- Bundle lid-related attributes into `LiddabilityDescription` and `LiddabilityDescriptor`.
"""

from typing import Literal

from pydantic import Field

from ...grid.v1 import GridDescription, GridDescriptor
from ...liddability.v1 import LiddabilityDescription, LiddabilityDescriptor
from ...well.v1 import WellDescription, WellDescriptor
from ..base.labware_description.v2 import BaseLabwareDescriptionV2, BaseLabwareDescriptorV2

grid_description = "Grid defining the well layout on the plate."
well_description = (
    "Description of a single well on the plate, which is assumed to be shared by all wells."
)
liddability_description = (
    "Description of whether or not the plate is liddable, where, and by what lid."
)


class WellPlateDescription(BaseLabwareDescriptionV2):
    """Description of a well plate.

    :note: The exception to the 'no optional attributes' rule for ``***Description`` classes
    is `lid_offset` and `lid`. These attributes default to None, assuming that a described
    labware has no lid.
    """

    type: Literal["WellPlate"] = "WellPlate"
    schema_version: Literal[5] = 5

    grid: GridDescription = Field(
        description=grid_description,
    )
    well: WellDescription = Field(
        description=well_description,
    )
    liddability: LiddabilityDescription = Field(
        description=liddability_description,
    )


class WellPlateDescriptor(BaseLabwareDescriptorV2):
    """:class:``WellPlateDescription`` with optional parameters."""

    type: Literal["WellPlate"] = "WellPlate"
    schema_version: Literal[5] = 5

    grid: GridDescriptor | None = Field(
        default=None,
        description=grid_description,
    )
    well: WellDescriptor | None = Field(
        default=None,
        description=well_description,
    )
    liddability: LiddabilityDescriptor | None = Field(
        default=None,
        description=liddability_description,
    )
