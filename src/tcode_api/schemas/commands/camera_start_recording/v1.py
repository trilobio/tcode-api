from typing import Literal

from pydantic import Field

from ...common.value_with_units import ValueWithUnits
from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class CAMERA_START_RECORDING(BaseRobotSpecificTCodeCommandV1):
    """Start a video recording on one of the target robot's USB cameras.

    Recording continues asynchronously on the robot while the script keeps executing,
    until stopped with :class:``CAMERA_STOP_RECORDING`` or ``max_duration`` elapses.
    The recording is stored on the robot by the trilo-cam service.
    """

    type: Literal["CAMERA_START_RECORDING"] = "CAMERA_START_RECORDING"
    schema_version: Literal[1] = 1

    camera_name: str = Field(
        description=("Name of the robot camera to use; expects a value from :class:``CameraName``.")
    )

    max_duration: ValueWithUnits | None = Field(
        default=None,
        description=(
            "Maximum recording duration; expects time units. When ``None``, the trilo-cam "
            "service default applies. The service clamps this to its hard maximum."
        ),
    )

    label: str | None = Field(
        default=None,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$",
        description=(
            "Optional label recorded into the recording filename on the robot; media can "
            "later be filtered by label. Must be filesystem-safe."
        ),
    )
