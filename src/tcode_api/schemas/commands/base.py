"""Base classes for the TCode command set."""

from abc import ABC

from pydantic import Field

from ..base import BaseSchemaVersionedModel
from ..common.docs import TypeField


class BaseTCodeCommand(BaseSchemaVersionedModel, ABC):
    """Base schema shared by all TCode commands in the TCODE discriminated union.

    :raises ValidatorError: ``ValidatorErrorCode.INTERNAL_ERROR`` if any unexpected error occurs
        during validation. If this occurs, file an issue on
        https://github.com/trilobio/tcode-api/issues.
    """

    type: TypeField


class BaseRobotSpecificTCodeCommand(BaseTCodeCommand, ABC):
    """Base schema shared by all TCode commands that are specific to a robot.

    Commands subclassing this class target a single robot with the specified ``robot_id``.
    """

    robot_id: str = Field(
        description=(
            "Identifier of the robot targeted by this command, "
            "previously defined with the :class:``ADD_ROBOT`` command."
        ),
    )
