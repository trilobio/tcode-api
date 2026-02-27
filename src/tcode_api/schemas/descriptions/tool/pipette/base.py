"""Base classes for descriptions and descriptors of pipette tool entities."""

from abc import ABC

from pydantic import Field

from ....common.value_with_units import ValueWithUnits
from ..base import BaseToolDescriptor


class BasePipetteDescriptor(BaseToolDescriptor, ABC):
    """Base schema shared by all models in the PipetteDescriptor union."""

    min_volume: ValueWithUnits | None = Field(
        default=None,
        description=(
            "Minimum volume that the pipette can handle while maintianing promised tolerances. "
            "expects volume units (e.g. ul)."
        ),
    )
    max_volume: ValueWithUnits | None = Field(
        default=None,
        description=(
            "Maximum volume that the pipette can hold (spec, not reality). "
            "expects volume units (e.g. ul)."
        ),
    )
    max_speed: ValueWithUnits | None = Field(
        default=None,
        description=(
            "Maximum speed that the pipette can move fluid; "
            "expects volume per time units (e.g. ul/s)."
        ),
    )
