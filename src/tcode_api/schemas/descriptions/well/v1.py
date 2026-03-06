"""Reference: https://trilobio.atlassian.net/wiki/spaces/SD/pages/350027782/User+Labware+Definitions"""

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
            "Distance from the top of the well to the bottom of the inside of the well. "
            "expects length units"
        ),
    ),
]

well_shape_field_docstring = (
    "The primary cross-sectional shape of the well, typically the shape of the opening."
)

bottom_shape_field_docstring = "The geometry of the bottom of the well. "


class WellDescriptionV1(BaseDescriberWithTags):
    """Description of a well in a labware."""

    type: Literal["Well"] = "Well"
    schema_version: Literal[1] = 1

    depth: DepthField
    shape: WellShapeDescription = Field(
        description=well_shape_field_docstring,
    )
    bottom_shape: WellBottomShapeDescription = Field(
        description=bottom_shape_field_docstring,
    )
    min_volume: MinVolumeField
    max_volume: MaxVolumeField


class WellDescriptorV1(BaseDescriberWithTags):
    """:class:``WellDescription`` with optional parameters."""

    type: Literal["Well"] = "Well"
    schema_version: Literal[1] = 1

    depth: DepthField | None = None
    shape: WellShapeDescriptor | None = Field(
        default=None,
        description=well_shape_field_docstring,
    )
    bottom_shape: WellBottomShapeDescriptor | None = Field(
        default=None,
        description=bottom_shape_field_docstring,
    )
    min_volume: MinVolumeField | None = None
    max_volume: MaxVolumeField | None = None
