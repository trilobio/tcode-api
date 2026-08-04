"""BaseRobotSpecificTCodeCommand v1."""

from abc import ABC

from pydantic import Field

from ..tcode_command.v1 import BaseTCodeCommandV1


class BaseRobotSpecificTCodeCommandV1(BaseTCodeCommandV1, ABC):
    """Base schema shared by all TCode commands that are specific to a robot.

    Commands subclassing this class target a single robot with the specified ``robot_id``.
    """

    robot_id: str = Field(
        description=(
            "Identifier of the robot targeted by this command, "
            "previously defined with the :class:``ADD_ROBOT`` command."
        ),
    )
