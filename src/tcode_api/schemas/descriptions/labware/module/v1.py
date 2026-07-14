from typing import Annotated, Literal

from pydantic import Field

from ....common.value_with_units import ValueWithUnits
from ..base import BaseLabwareDescription, BaseLabwareDescriptor

HolderXField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "X translation from the module's base to its labware holder (where a held "
            "labware's base sits). Expects length units."
        ),
    ),
]

HolderYField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "Y translation from the module's base to its labware holder (where a held "
            "labware's base sits). Expects length units."
        ),
    ),
]

HolderZField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "Z translation from the module's base to its labware holder (where a held "
            "labware's base sits). Expects length units."
        ),
    ),
]

HolderAField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "Rotation of the module's labware holder about the z-axis. Applied as "
            "Rz(a)·Ry(b)·Rx(c). Expects angle units."
        ),
    ),
]

HolderBField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "Rotation of the module's labware holder about the y-axis. Applied as "
            "Rz(a)·Ry(b)·Rx(c). Expects angle units."
        ),
    ),
]

HolderCField = Annotated[
    ValueWithUnits,
    Field(
        description=(
            "Rotation of the module's labware holder about the x-axis. Applied as "
            "Rz(a)·Ry(b)·Rx(c). Expects angle units."
        ),
    ),
]

LiftableField = Annotated[
    bool,
    Field(
        description=(
            "Whether labware held by the module can be grasped with a LIFT grasp. "
            "Set to False for modules whose body blocks the gripper's lift paddles, "
            "in which case held labware must be PINCH-grasped."
        ),
    ),
]


class ModuleDescription(BaseLabwareDescription):
    """Description of a deck-slot module (e.g. a magdeck or riser).

    A module sits in a deck slot and holds other labware at an offset pose,
    so labware resting on it (and everything derived from the labware's pose,
    e.g. well locations and gripper pick/place targets) is raised relative to
    the deck slot.
    """

    type: Literal["Module"] = "Module"
    schema_version: Literal[1] = 1

    holder_x: HolderXField
    holder_y: HolderYField
    holder_z: HolderZField
    holder_a: HolderAField
    holder_b: HolderBField
    holder_c: HolderCField

    liftable: LiftableField = True


class ModuleDescriptor(BaseLabwareDescriptor):
    """:class:``ModuleDescription`` with optional parameters."""

    type: Literal["Module"] = "Module"
    schema_version: Literal[1] = 1

    holder_x: HolderXField | None = None
    holder_y: HolderYField | None = None
    holder_z: HolderZField | None = None
    holder_a: HolderAField | None = None
    holder_b: HolderBField | None = None
    holder_c: HolderCField | None = None

    liftable: LiftableField | None = None
