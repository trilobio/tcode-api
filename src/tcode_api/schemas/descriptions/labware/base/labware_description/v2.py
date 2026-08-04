"""BaseLabwareDescription & BaseLabwareDescriptor v2.

- Adds the required (resp. optional) `pinchable` field.
"""

from abc import ABC
from typing import Annotated

from pydantic import Field

from .v1 import BaseLabwareDescriptionV1, BaseLabwareDescriptorV1

PinchableField = Annotated[
    bool,
    Field(description="Whether the labware can be lifted by a Trilobot using a pinch grip."),
]


class BaseLabwareDescriptionV2(BaseLabwareDescriptionV1, ABC):
    """Version 2 of :class:`BaseLabwareDescriptionV1`, adding the required ``pinchable`` field."""

    pinchable: PinchableField


class BaseLabwareDescriptorV2(BaseLabwareDescriptorV1, ABC):
    """Version 2 of :class:`BaseLabwareDescriptorV1`, adding the optional ``pinchable`` field."""

    pinchable: PinchableField | None = None
