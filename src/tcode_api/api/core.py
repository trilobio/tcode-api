"""TCode API definitions, implemented with Pydantic."""

from __future__ import annotations

from typing import Literal

from pint import Unit
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

    def __str__(self) -> str:
        return f"{self.magnitude} {self.units}"

    def to(self, units: str | Unit) -> ValueWithUnits:
        """Convert to the specified units.

        :note: Units implementation in python uses `pint` under the hood.
        :param units: The units to convert to.

        """
        if units == self.units:
            return self.model_copy()
        if str(units) == self.units:
            return self.model_copy()
        pint_quantity = Q_(self.magnitude, self.units).to(units)
        return ValueWithUnits(magnitude=pint_quantity.magnitude, units=str(units))

    def __mul__(self, other: int | float) -> ValueWithUnits:
        """Multiply the ValueWithUnits by a scalar.

        :param other: The scalar to multiply by.

        :return: A new ValueWithUnits representing the product.
        """
        try:
            other = float(other)
        except (TypeError, ValueError):
            return NotImplemented

        return ValueWithUnits(magnitude=self.magnitude * other, units=self.units)

    def __rmul__(self, other: int | float) -> ValueWithUnits:
        """Multiply the ValueWithUnits by a scalar.

        :param other: The scalar to multiply by.

        :return: A new ValueWithUnits representing the product.
        """
        return self.__mul__(other)

    def __add__(self, other: object) -> ValueWithUnits:
        """Add two ValueWithUnits together, converting units as necessary.

        :note: the units of the returned ValueWithUnits will be the units of the left-hand side.

        :param other: The other ValueWithUnits to add.

        :return: A new ValueWithUnits representing the sum.
        """
        if not isinstance(other, ValueWithUnits):
            return NotImplemented

        if other.units == self.units:
            # This logic path is approx. 3x faster
            return ValueWithUnits(
                magnitude=self.magnitude + other.magnitude, units=self.units
            )

        pint_quantity = Q_(self.magnitude, self.units) + Q_(
            other.magnitude, other.units
        )
        return ValueWithUnits(
            magnitude=pint_quantity.magnitude, units=str(pint_quantity.units)
        )

    def __sub__(self, other: object) -> ValueWithUnits:
        """Subtract two ValueWithUnits, converting units as necessary.

        :note: the units of the returned ValueWithUnits will be the units of the left-hand side.

        :param other: The other ValueWithUnits to subtract.

        :return: A new ValueWithUnits representing the difference.
        """
        if not isinstance(other, ValueWithUnits):
            return NotImplemented

        if other.units == self.units:
            # This logic path is approx. 3x faster
            return ValueWithUnits(
                magnitude=self.magnitude - other.magnitude, units=self.units
            )

        pint_quantity = Q_(self.magnitude, self.units) - Q_(
            other.magnitude, other.units
        )
        return ValueWithUnits(
            magnitude=pint_quantity.magnitude, units=str(pint_quantity.units)
        )

    def __eq__(self, other: object) -> bool:
        """Check equality between two ValueWithUnits, converting units as necessary.

        :param other: The other ValueWithUnits to compare.

        :return: True if the two ValueWithUnits are equal, False otherwise.
        """
        if not isinstance(other, ValueWithUnits):
            return NotImplemented

        if other.units == self.units:
            return self.magnitude == other.magnitude
        return Q_(self.magnitude, self.units) == Q_(other.magnitude, other.units)

    def __neg__(self) -> ValueWithUnits:
        """Negate the ValueWithUnits.

        :return: A new ValueWithUnits representing the negation.
        """
        return ValueWithUnits(magnitude=-self.magnitude, units=self.units)

    def __lt__(self, other: object) -> bool:
        """Check if this ValueWithUnits is less than another, converting units as necessary.

        :param other: The other ValueWithUnits to compare.

        :return: True if this ValueWithUnits is less than the other, False otherwise.
        """
        if not isinstance(other, ValueWithUnits):
            return NotImplemented

        if other.units == self.units:
            return self.magnitude < other.magnitude

        return Q_(self.magnitude, self.units) < Q_(other.magnitude, other.units)

    def __le__(self, other: object) -> bool:
        """Check if this ValueWithUnits is less than or equal to another, converting units as necessary.

        :param other: The other ValueWithUnits to compare.

        :return: True if this ValueWithUnits is less than or equal to the other, False otherwise.
        """
        if not isinstance(other, ValueWithUnits):
            return NotImplemented

        if other.units == self.units:
            return self.magnitude <= other.magnitude

        return Q_(self.magnitude, self.units) <= Q_(other.magnitude, other.units)

    def __gt__(self, other: object) -> bool:
        """Check if this ValueWithUnits is greater than another, converting units as necessary.

        :param other: The other ValueWithUnits to compare.

        :return: True if this ValueWithUnits is greater than the other, False otherwise.
        """
        if not isinstance(other, ValueWithUnits):
            return NotImplemented

        if other.units == self.units:
            return self.magnitude > other.magnitude

        return Q_(self.magnitude, self.units) > Q_(other.magnitude, other.units)

    def __ge__(self, other: object) -> bool:
        """Check if this ValueWithUnits is greater than or equal to another, converting units as necessary.

        :param other: The other ValueWithUnits to compare.

        :return: True if this ValueWithUnits is greater than or equal to the other, False otherwise.
        """
        if not isinstance(other, ValueWithUnits):
            return NotImplemented

        if other.units == self.units:
            return self.magnitude >= other.magnitude

        return Q_(self.magnitude, self.units) >= Q_(other.magnitude, other.units)


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
