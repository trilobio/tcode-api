# Protocol Designer starts the LabwareDescriptorBase at V3, so this increment has no changes.
from typing import Annotated, Literal

from pydantic import Field

from ....common.value_with_units import ValueWithUnits
from ...grid.v1 import GridDescription, GridDescriptor
from ...well.v1 import WellDescription, WellDescriptor
from ..base import BaseLabwareDescription, BaseLabwareDescriptor
from ..lid.v3 import LidDescription, LidDescriptor

LidOffsetField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "The offset from the top of the labware to the bottom of the lid. "
            "Expects length units. Only applicable if the labware has a lid."
        ),
    ),
]
grid_description = "Grid defining the well layout on the plate."
well_description = (
    "Description of a single well on the plate, which is assumed to be shared by all wells."
)
lid_description = "Description of the lid, or None if the plate is un-liddable."


class WellPlateDescription(BaseLabwareDescription):
    """Description of a well plate.

    :note: The exception to the 'no optional attributes' rule for ``***Description`` classes
    is `lid_offset` and `lid`. These attributes default to None, assuming that a described
    labware has no lid.
    """

    type: Literal["WellPlate"] = "WellPlate"
    schema_version: Literal[3] = 3

    grid: GridDescription = Field(
        description=grid_description,
    )
    well: WellDescription = Field(
        description=well_description,
    )

    # Lid parameters
    lid_offset: LidOffsetField | None = None
    lid: LidDescription | None = Field(
        default=None,
        description=lid_description,
    )


class WellPlateDescriptor(BaseLabwareDescriptor):
    """:class:``WellPlateDescription`` with optional parameters."""

    type: Literal["WellPlate"] = "WellPlate"
    schema_version: Literal[3] = 3

    grid: GridDescriptor | None = Field(
        default=None,
        description=grid_description,
    )
    well: WellDescriptor | None = Field(
        default=None,
        description=well_description,
    )
    lid_offset: LidOffsetField | None = None
    lid: LidDescriptor | None = Field(
        default=None,
        description=lid_description,
    )
