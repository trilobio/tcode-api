from typing import Literal

from pydantic import Field

from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class CAMERA_TAKE_PICTURE(BaseRobotSpecificTCodeCommandV1):
    """Capture a still image with one of the target robot's USB cameras.

    The image is stored on the robot by the trilo-cam service under a timestamped
    filename. Set ``save_directory`` to also download the image to the fleet controller.
    """

    type: Literal["CAMERA_TAKE_PICTURE"] = "CAMERA_TAKE_PICTURE"
    schema_version: Literal[1] = 1

    camera_name: str = Field(
        description=("Name of the robot camera to use; expects a value from :class:``CameraName``.")
    )

    save_directory: str | None = Field(
        default=None,
        description=(
            "Fleet-controller directory to save the captured image into. When ``None``, "
            "the image is only stored on the robot."
        ),
    )
