"""BaseLabwareDescription & BaseLabwareDescriptor v2.

- Adds the required (resp. optional) `pinchable` field.
- Adds the optional `pinch_offset_transform` field.
"""

from abc import ABC
from typing import Annotated, Self

from pydantic import Field, model_validator

from ......types import Matrix
from .v1 import BaseLabwareDescriptionV1, BaseLabwareDescriptorV1

PinchableField = Annotated[
    bool,
    Field(description="Whether the labware can be lifted by a Trilobot using a pinch grip."),
]

PinchOffsetTransformField = Annotated[
    Matrix,
    Field(
        description=(
            "Transform from the center of the labware's footprint to the center of the"
            " pinchable location on the labware. Must be provided if `pinchable` is `True`."
        ),
    ),
]


class BaseLabwareDescriptionV2(BaseLabwareDescriptionV1, ABC):
    """Version 2 of :class:`BaseLabwareDescriptionV1`, adding the required ``pinchable`` field."""

    pinchable: PinchableField
    pinch_offset_transform: PinchOffsetTransformField | None = None

    @model_validator(mode="after")
    def validate_pinch_data(self) -> Self:
        """Validate that if the labware is pinchable, a pinch offset transform is provided."""
        if self.pinchable and self.pinch_offset_transform is None:
            raise ValueError("If `pinchable` is True, `pinch_offset_transform` must be provided.")
        elif not self.pinchable and self.pinch_offset_transform is not None:
            raise ValueError(
                "If `pinchable` is False, `pinch_offset_transform` must not be provided."
            )
        return self


class BaseLabwareDescriptorV2(BaseLabwareDescriptorV1, ABC):
    """Version 2 of :class:`BaseLabwareDescriptorV1`, adding the optional ``pinchable`` field."""

    pinchable: PinchableField | None = None
    pinch_offset_transform: PinchOffsetTransformField | None = None
