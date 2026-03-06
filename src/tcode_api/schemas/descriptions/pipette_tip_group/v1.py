"""
:note: The class ``PipetteTipGroupDescription`` doesn't exist because semantially, we ONLY match tip groups.
You cannot specify explicitly the entire set of feature for a set of tips that you want to create. Instead, use PipetteTipDescription and make a bunch of tips.
"""

from typing import Literal

from pydantic import Field, PositiveInt

from ...base import BaseSchemaVersionedModel
from ...common.docs import NamedTags, Tags


class PipetteTipGroupDescriptorV1(BaseSchemaVersionedModel):
    """Grid layout of pipette tips."""

    type: Literal["PipetteTipGroup"] = "PipetteTipGroup"
    schema_version: Literal[1] = 1

    row_count: PositiveInt = Field(
        description=(
            "Number of rows of pipette tips in this group. Rows are referenced relative to the "
            "tip group's coordinate system, NOT the labware's coordinate system. "
            "e.g. a 1*8 pipette tip group can lie along the column or row of a 96 tip rack."
        ),
    )
    column_count: PositiveInt = Field(
        description=(
            "Number of columns of pipette tips in this group. Columns are referenced relative to the "
            "tip group's coordinate system, NOT the labware's coordinate system. "
            "e.g. a 1*8 pipette tip group can lie along the column or row of a 96 tip rack."
        ),
    )
    pipette_tip_tags: Tags = Field(
        default_factory=list,
        description=(
            "Tags to apply to all pipette tips in this group. For a pipette tip group to "
            "match this descriptor, all pipette tips in the group must have all of these tags, "
            "but may have additional tags as well."
        ),
    )
    pipette_tip_named_tags: NamedTags = Field(
        default_factory=dict,
        description=(
            "Named tags to apply to all pipette tips in this group. For a pipette tip group to "
            "match this descriptor, all pipette tips in the group must have all of these named tags "
            "with matching values, but may have additional named tags as well."
        ),
    )
