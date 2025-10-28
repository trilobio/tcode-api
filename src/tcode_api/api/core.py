"""TCode API definitions, implemented with Pydantic."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from tcode_api.units import Q_


class _ConfiguredBaseModel(BaseModel):
    """pydantic.BaseModel with configuration to apply to all TCode data structures.

    All TCode data structures should inherit from this class to ensure consistent
    configuration.
    """

    model_config = ConfigDict(strict=True, extra="ignore")


class _BaseModelWithId(_ConfiguredBaseModel):
    """TCode-configured BaseModel with an ID field."""

    id: str


class ValueWithUnits(_ConfiguredBaseModel):
    """A numeric value with associated units.

    :note: The following values are all equivalent:

        ``ValueWithUnits(magnitude=0.005, units="L")``

        ``ValueWithUnits(magnitude=5, units="mL")``

        ``ValueWithUnits(magnitude=5000, units="uL")``

        ``ValueWithUnits(magnitude=5000, units="mm³")``

    :note: In the python implementation, ``pint`` is used to resolve units. see `tcode_api.units`.
    """

    type: Literal["ValueWithUnits"] = "ValueWithUnits"
    magnitude: float
    units: str

    def __hash__(self):
        # TODO (connor): Mia mentioned that this can produce collisions, fix.
        return hash(self.magnitude) ^ hash(self.units)

    def __str__(self):
        return f"{self.magnitude} {self.units}"

    def to(self, units: str) -> "ValueWithUnits":
        """Convert to the specified units.

        :note: Units implementation in python uses `pint` under the hood.
        :param units: The units to convert to.

        """
        pint_quantity = Q_(self.magnitude, self.units).to(units)
        return ValueWithUnits(magnitude=pint_quantity.magnitude, units=units)


def _verify_positive_nonzero_int(value: int) -> int:
    """Validator to ensure the value is a positive non-zero integer.

    :param value: The integer to validate.
    :raises ValueError: If the value is not a positive non-zero integer.
    :return: The validated integer.
    """
    if value <= 0:
        raise ValueError(f"Value must be > 0, not {value}")

    return value


# Shapes
class CircleDescription(_ConfiguredBaseModel):
    """Description of a circle."""

    type: Literal["Circle"] = "Circle"
    diameter: ValueWithUnits


class CircleDescriptor(_ConfiguredBaseModel):
    """CircleDescription with optional parameters."""

    type: Literal["Circle"] = "Circle"
    diameter: ValueWithUnits | None = None


class AxisAlignedRectangleDescription(_ConfiguredBaseModel):
    """Description of an axis-aligned rectangle.

    :note: X and Y lengths are measured in the coordinate system of the parent labware,
        to avoid ambiguity when referring to the "length" or "width" of a rectangle.
    """

    type: Literal["AxisAlignedRectangle"] = "AxisAlignedRectangle"
    x_length: ValueWithUnits
    y_length: ValueWithUnits


class AxisAlignedRectangleDescriptor(_ConfiguredBaseModel):
    """AxisAlignedRectangleDescription with optional parameters."""

    type: Literal["AxisAlignedRectangle"] = "AxisAlignedRectangle"
    x_length: ValueWithUnits | None = None
    y_length: ValueWithUnits | None = None
