"""Shared documentation annotations used across TCode API schemas, and standardized here."""

from typing import Annotated

from pydantic import Field

from .value_with_units import ValueWithUnits

Tags = Annotated[
    list[str],
    Field(
        default_factory=list,
        description="List of additional string tags attached to the entity.",
    ),
]

NamedTags = Annotated[
    dict[str, str | int | float | bool],
    Field(
        default_factory=dict,
        description=(
            "Map of names and values of named tags attached to the entity. ",
            "Values can be strings, numbers, or booleans.",
        ),
    ),
]

MinVolumeField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "The minimum working fluid volume, as recommended by the manufacturer.",
            "expects volume units",
        ),
    ),
]

MaxVolumeField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "The maximum working fluid volume, as recommended by the manufacturer.",
            "expects volume units",
        ),
    ),
]

TypeField = Annotated[
    str,
    Field(
        description=(
            "Discriminator field; ",
            "overridden in subclass with class name as string sans versioning information.",
            'ex. ``class MyLabwareHolderV1(BaseLabwareHolder): type: Literal["MyLabwareHolder"]`` = "MyLabwareHolder"',
        ),
    ),
]

LabwareIdField = Annotated[
    str,
    Field(
        description=(
            "Identifier for a target piece of ANSI-SLAS-compatible labware, ",
            "assigned by previous :class:``ADD_LABWARE`` command.",
        ),
    ),
]

LidIdField = Annotated[
    str,
    Field(
        description=(
            "Identifier for the targeted lid of a piece of ANSI-SLAS-compatible labware, ",
            "assigned by previous :class:``ADD_LABWARE`` command via the ``lid_id`` argument.",
        ),
    ),
]

PipetteTipGroupIdField = Annotated[
    str,
    Field(
        description=(
            "Identifier for a target pipette tip group, assigned by previous :class:``ADD_PIPETTE_TIP_GROUP`` command."
        ),
    ),
]

ToolIdField = Annotated[
    str,
    Field(
        description=(
            "Identifier for a target robot tool, assigned by previous :class:``ADD_TOOL`` command."
        ),
    ),
]
