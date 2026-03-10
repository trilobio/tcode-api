from abc import ABC
from typing import Annotated

from pydantic import Field

from ...common.value_with_units import ValueWithUnits
from ..base import BaseDescriberWithTags

XLengthField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "The labware's extent along the x-axis of it's coordinate system. Expects length units.",
        ),
    ),
]

YLengthField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "The labware's extent along the y-axis of it's coordinate system. Expects length units.",
        ),
    ),
]

ZLengthField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "The labware's extent along the z-axis of it's coordinate system. Expects length units.",
        ),
    ),
]


class BaseLabwareDescription(BaseDescriberWithTags, ABC):
    """Base schema shared by all labware in the :class:``Labware`` discriminated union.

    :note: Using [x|y|z]_length is intended to avoid the semantic ambiguity of "length" vs "width"
    """

    x_length: XLengthField
    y_length: YLengthField
    z_length: ZLengthField


class BaseLabwareDescriptor(BaseDescriberWithTags, ABC):
    """Base schema shared by all labware descriptors in the :class:``LabwareDescriptor`` discriminated union."""

    x_length: XLengthField | None = None
    y_length: YLengthField | None = None
    z_length: ZLengthField | None = None
