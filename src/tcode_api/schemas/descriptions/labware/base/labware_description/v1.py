"""BaseLabwareDescription & BaseLabwareDescriptor v1.

:note: Description and Descriptor are versioned together (not split into separate models) since
    they represent the same logical entity and their versions bump in lockstep.
"""

from abc import ABC
from typing import Annotated

from pydantic import Field

from .....common.value_with_units import ValueWithUnits
from ....base.describer_with_tags.v1 import BaseDescriberWithTagsV1

XLengthField = Annotated[
    ValueWithUnits,
    Field(
        description="The labware's extent along the x-axis of it's coordinate system. Expects length units.",
    ),
]

YLengthField = Annotated[
    ValueWithUnits,
    Field(
        description="The labware's extent along the y-axis of it's coordinate system. Expects length units.",
    ),
]

ZLengthField = Annotated[
    ValueWithUnits,
    Field(
        description="The labware's extent along the z-axis of it's coordinate system. Expects length units.",
    ),
]


class BaseLabwareDescriptionV1(BaseDescriberWithTagsV1, ABC):
    """Base schema shared by all labware in the :class:``Labware`` discriminated union.

    :note: Using [x|y|z]_length is intended to avoid the semantic ambiguity of "length" vs "width"
    """

    x_length: XLengthField
    y_length: YLengthField
    z_length: ZLengthField


class BaseLabwareDescriptorV1(BaseDescriberWithTagsV1, ABC):
    """Base schema shared by all labware descriptors in the :class:``LabwareDescriptor`` discriminated union."""

    x_length: XLengthField | None = None
    y_length: YLengthField | None = None
    z_length: ZLengthField | None = None
