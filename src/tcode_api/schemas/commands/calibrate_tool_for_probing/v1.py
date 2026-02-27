from typing import Literal

from pydantic import Field

from ..base import BaseRobotSpecificTCodeCommand


class CALIBRATE_TOOL_FOR_PROBING_V1(BaseRobotSpecificTCodeCommand):
    """Calibrate the target robot's currently held tool for probing."""

    type: Literal["CALIBRATE_TOOL_FOR_PROBING"] = "CALIBRATE_TOOL_FOR_PROBING"
    schema_version: Literal[1] = 1

    z_only: bool = Field(
        description=(
            "When true, calibrate only for z-axis probing. " "When false, calibrate x, y, and z."
        )
    )

    persistent: bool = Field(
        default=False,
        description="Whether calibration should persist beyond the current session.",
    )
