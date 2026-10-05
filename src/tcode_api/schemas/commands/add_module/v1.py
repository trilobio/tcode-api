from typing import Annotated, Literal

from pydantic import Field

from ...descriptions.labware.module.latest import ModuleDescriptor
from ...location.location_as_labware_holder.latest import LocationAsLabwareHolder
from ...location.location_relative_to_robot.latest import LocationRelativeToRobot
from ..base.tcode_command.v1 import BaseTCodeCommandV1

ModuleLocation = Annotated[
    LocationAsLabwareHolder | LocationRelativeToRobot,
    Field(
        discriminator="type",
        description=(
            "Where the module sits. A LocationAsLabwareHolder places it in a deck slot, so it "
            "can be moved between slots like any other labware. A LocationRelativeToRobot "
            "fixes it at a pose relative to the robot's root node, for modules that are bolted "
            "down and never moved."
        ),
    ),
]


class ADD_MODULE(BaseTCodeCommandV1):
    """Register a module and assign it the given id.

    A module is a deck-side device that both holds labware at an offset pose and accepts
    commands of its own. Registering it gives it an execution queue, so work addressed to the
    module is ordered against the module's other work rather than against a robot's. Use
    ``depends_on`` and ``sync_group`` on the schedule envelope to order module work against
    robot motion.

    :raises ValidatorError: ``ValidatorErrorCode.ID_EXISTS`` if ``id`` is already registered.
    """

    type: Literal["ADD_MODULE"] = "ADD_MODULE"
    schema_version: Literal[1] = 1

    id: str = Field(
        description=(
            "Identifier to assign to the resolved module. "
            "This id is used in subsequent commands to reference this module."
        )
    )
    descriptor: ModuleDescriptor = Field(
        description="Minimal descriptor of the desired module; resolved on the fleet."
    )
    location: ModuleLocation
