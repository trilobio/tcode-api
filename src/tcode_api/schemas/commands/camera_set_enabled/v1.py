from typing import Literal

from pydantic import Field

from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class CAMERA_SET_ENABLED(BaseRobotSpecificTCodeCommandV1):
    """Power one of the target robot's USB cameras on or off.

    Powering a camera on takes a few seconds before it can capture; the trilo-cam
    service reports the camera as running once ready.
    """

    type: Literal["CAMERA_SET_ENABLED"] = "CAMERA_SET_ENABLED"
    schema_version: Literal[1] = 1

    camera_name: str = Field(
        description=("Name of the robot camera to use; expects a value from :class:``CameraName``.")
    )

    enabled: bool = Field(description="Whether the camera should be powered on.")
