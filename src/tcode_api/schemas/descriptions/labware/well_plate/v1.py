from typing import Annotated, Literal

from pydantic import Field

from ....common.value_with_units import ValueWithUnits
from ...grid.v1 import GridDescriptionV1, GridDescriptorV1
from ...well.v1 import WellDescriptionV1, WellDescriptorV1
from ..base import BaseLabwareDescription, BaseLabwareDescriptor
from ..lid.v1 import LidDescriptionV1, LidDescriptorV1

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


class WellPlateDescriptionV1(BaseLabwareDescription):
    """Description of a well plate.

    :note: The exception to the 'no optional attributes' rule for ``***Description`` classes
    is `lid_offset` and `lid`. These attributes default to None, assuming that a described
    labware has no lid.
    """

    type: Literal["WellPlate"] = "WellPlate"
    schema_version: Literal[1] = 1

    grid: GridDescriptionV1 = Field(
        description=grid_description,
    )
    well: WellDescriptionV1 = Field(
        description=well_description,
    )

    # Lid parameters
    lid_offset: LidOffsetField | None = None
    lid: LidDescriptionV1 | None = Field(
        None,
        description=lid_description,
    )


class WellPlateDescriptorV1(BaseLabwareDescriptor):
    """:class:``WellPlateDescription`` with optional parameters."""

    type: Literal["WellPlate"] = "WellPlate"
    schema_version: Literal[1] = 1

    grid: GridDescriptorV1 | None = Field(
        None,
        description=grid_description,
    )
    well: WellDescriptorV1 | None = Field(
        None,
        description=well_description,
    )
    lid_offset: LidOffsetField | None = None
    lid: LidDescriptorV1 | None = Field(
        None,
        description=lid_description,
    )
