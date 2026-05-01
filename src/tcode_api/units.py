"""Pint integration for units management."""

from pint import UnitRegistry

ureg: UnitRegistry = UnitRegistry()
Q_ = ureg.Quantity
