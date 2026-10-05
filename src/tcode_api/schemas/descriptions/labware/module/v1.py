from typing import Annotated, Literal

from pydantic import Field

from tcode_api.types import Matrix

from ..base.labware_description.v2 import BaseLabwareDescriptionV2, BaseLabwareDescriptorV2

HolderTransformField = Annotated[
    Matrix,
    Field(
        description=(
            "Transform from the module's base to its labware holder, where a held labware's "
            "base sits."
        ),
    ),
]

SupportsLiftableLabwareField = Annotated[
    bool,
    Field(
        description=(
            "Whether labware held by the module can be grasped with a LIFT grasp. The module "
            "itself is never lifted; this describes what it permits of the labware it holds. "
            "Set to False for modules whose body blocks the gripper's lift paddles, in which "
            "case held labware must be PINCH-grasped."
        ),
    ),
]


class ModuleDescription(BaseLabwareDescriptionV2):
    """Description of a deck-slot module (e.g. a magdeck or riser).

    A module sits in a deck slot and holds other labware at an offset pose,
    so labware resting on it (and everything derived from the labware's pose,
    e.g. well locations and gripper pick/place targets) is raised relative to
    the deck slot.
    """

    type: Literal["Module"] = "Module"
    schema_version: Literal[1] = 1

    holder_transform: HolderTransformField

    supports_liftable_labware: SupportsLiftableLabwareField


class ModuleDescriptor(BaseLabwareDescriptorV2):
    """:class:``ModuleDescription`` with optional parameters."""

    type: Literal["Module"] = "Module"
    schema_version: Literal[1] = 1

    holder_transform: HolderTransformField | None = None

    supports_liftable_labware: SupportsLiftableLabwareField | None = None
