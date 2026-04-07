from typing import Literal

from pydantic import Field

from ...descriptions.robot.v1 import RobotDescriptor
from ..base import BaseTCodeCommand


class ADD_ROBOT(BaseTCodeCommand):
    """Find a matching robot on the fleet and assign it the given id."""

    type: Literal["ADD_ROBOT"] = "ADD_ROBOT"
    schema_version: Literal[1] = 1

    id: str = Field(
        description=(
            "Identifier to assign to the resolved robot. "
            "This id is used in subsequent commands to reference this robot."
        )
    )

    descriptor: RobotDescriptor = Field(
        description="Minimal descriptor of the desired robot; resolved on the fleet."
    )
