"""Pint integration for units management."""

from pint import UnitRegistry

ureg = UnitRegistry()
Q_ = ureg.Quantity
