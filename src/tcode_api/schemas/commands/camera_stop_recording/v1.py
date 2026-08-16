from typing import Literal

from pydantic import Field

from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class CAMERA_STOP_RECORDING(BaseRobotSpecificTCodeCommandV1):
    """Stop the active video recording on one of the target robot's USB cameras.

    The recording is finalized and stored on the robot by the trilo-cam service.
    """

    type: Literal["CAMERA_STOP_RECORDING"] = "CAMERA_STOP_RECORDING"
    schema_version: Literal[1] = 1

    camera_name: str = Field(
        description=("Name of the robot camera to use; expects a value from :class:``CameraName``.")
    )
