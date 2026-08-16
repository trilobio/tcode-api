from typing import Literal

from pydantic import Field

from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class CAMERA_CONFIGURE(BaseRobotSpecificTCodeCommandV1):
    """Apply capture settings to one of the target robot's USB cameras.

    Only the provided fields are changed. Resolution and framerate changes are
    rejected by the trilo-cam service while the camera is recording.
    """

    type: Literal["CAMERA_CONFIGURE"] = "CAMERA_CONFIGURE"
    schema_version: Literal[1] = 1

    camera_name: str = Field(
        description=("Name of the robot camera to use; expects a value from :class:``CameraName``.")
    )

    resolution: list[int] | None = Field(
        default=None,
        min_length=2,
        max_length=2,
        description="Capture resolution as ``[width, height]`` in pixels.",
    )

    framerate: int | None = Field(
        default=None,
        description="Capture framerate in frames per second.",
    )

    controls: dict[str, int] | None = Field(
        default=None,
        description=(
            "Camera control values by name (e.g. ``brightness``), as exposed by the "
            "trilo-cam service settings endpoint."
        ),
    )
