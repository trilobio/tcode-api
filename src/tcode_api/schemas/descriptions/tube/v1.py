from typing import Annotated, Literal

from pydantic import Field

from ...common.docs import MaxVolumeField, MinVolumeField
from ...common.value_with_units import ValueWithUnits
from ..base import BaseDescriberWithTags
from ..union import WellShapeDescription, WellShapeDescriptor
from ..well_bottom.union import WellBottomShapeDescription, WellBottomShapeDescriptor

DepthField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "Distance from the top of the tube to the centered bottom of the tube. ",
            "expects length units",
        ),
    ),
]

bottom_shape_field_docstring = "The geometry of the bottom of the tube. "
shape_field_docstring = (
    "The primary cross-sectional shape of the tube; typically the shape of the opening"
)

TopHeightField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "The height of the tube cap above the top of the tube. ",
            "expects length units.",
        ),
    ),
]


class TubeDescriptionV1(BaseDescriberWithTags):
    """Description of a tube."""

    type: Literal["Tube"] = "Tube"
    schema_version: Literal[1] = 1

    depth: DepthField
    shape: WellShapeDescription = Field(
        description=shape_field_docstring,
    )
    bottom_shape: WellBottomShapeDescription = Field(
        description=bottom_shape_field_docstring,
    )
    min_volume: MinVolumeField
    max_volume: MaxVolumeField
    top_height: TopHeightField


class TubeDescriptorV1(BaseDescriberWithTags):
    """:class:``TubeDescription`` with optional parameters."""

    type: Literal["Tube"] = "Tube"
    schema_version: Literal[1] = 1

    depth: DepthField | None = None
    shape: WellShapeDescriptor | None = Field(
        default=None,
        description=shape_field_docstring,
    )
    bottom_shape: WellBottomShapeDescriptor | None = Field(
        default=None,
        description=bottom_shape_field_docstring,
    )
    min_volume: MinVolumeField | None = None
    max_volume: MaxVolumeField | None = None
    top_height: TopHeightField | None = None
