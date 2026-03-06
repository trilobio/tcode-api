from typing import Annotated, Literal

from pydantic import Field

from ...common.docs import MaxVolumeField, MinVolumeField
from ...common.value_with_units import ValueWithUnits
from ..base import BaseDescriberWithTags

HasFilterField = Annotated[
    bool,
    Field(
        description="Whether the pipette tip has an internal filter.",
    ),
]

HeightField = Annotated[
    ValueWithUnits,
    Field(
        description="total length of the pipette tip; expects length units",
    ),
]

FlangeHeightField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "The distance from the top of the pipette tip to the flange ",
            "which rests against the tip rack when the tip is racked; ",
            "expects length units",
        ),
    ),
]


class PipetteTipDescriptionV1(BaseDescriberWithTags):
    """Description of a pipette tip."""

    type: Literal["PipetteTip"] = "PipetteTip"
    schema_version: Literal[1] = 1

    has_filter: HasFilterField
    height: HeightField
    flange_height: FlangeHeightField
    max_volume: MaxVolumeField
    min_volume: MinVolumeField


class PipetteTipDescriptorV1(BaseDescriberWithTags):
    """:class:``PipetteTipDescription`` with optional parameters."""

    type: Literal["PipetteTip"] = "PipetteTip"
    schema_version: Literal[1] = 1

    has_filter: HasFilterField | None = None
    height: HeightField | None = None
    flange_height: FlangeHeightField | None = None
    max_volume: MaxVolumeField | None = None
    min_volume: ValueWithUnits | None = None
