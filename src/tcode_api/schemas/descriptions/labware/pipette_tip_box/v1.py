from typing import Annotated, Literal

from pydantic import Field

from ...grid.v1 import GridDescriptionV1, GridDescriptorV1
from ...pipette_tip.v1 import PipetteTipDescriptionV1, PipetteTipDescriptorV1
from ..base import BaseLabwareDescription, BaseLabwareDescriptor

grid_description = "Layout of the pipette tip box slots. typically an 8*12 grid for a 96 tip box."

pipette_tip_description = (
    "Description of the pipette tips used in the box. "
    "All pipette tips are assumed to be identical."
)
pipette_tip_layout_description = (
    "Specifies which slots contain pipette tips."
    "If not provided, it is assumed that all slots in the grid are filled with pipette tips."
)

FullField = Annotated[
    bool,
    Field(
        default=True,
        description="Whether or not the tip box is fully filled with tips.",
    ),
]


class PipetteTipBoxDescriptionV1(BaseLabwareDescription):
    """Description of a pipette tip box."""

    type: Literal["PipetteTipBox"] = "PipetteTipBox"
    schema_version: Literal[1] = 1

    grid: GridDescriptionV1 = Field(
        description=grid_description,
    )
    pipette_tip: PipetteTipDescriptionV1 = Field(
        description=pipette_tip_description,
    )
    full: FullField


class PipetteTipBoxDescriptorV1(BaseLabwareDescriptor):
    """PipetteTipBoxDescription with optional parameters."""

    type: Literal["PipetteTipBox"] = "PipetteTipBox"
    schema_version: Literal[1] = 1

    grid: GridDescriptorV1 | None = Field(
        default=None,
        description=grid_description,
    )
    pipette_tip: PipetteTipDescriptorV1 | None = Field(
        default=None,
        description=pipette_tip_description,
    )
    full: FullField | None = None
