from typing import Literal

from pydantic import Field

from ..base import BaseRobotSpecificTCodeCommand


class CALIBRATE_TOOL(BaseRobotSpecificTCodeCommand):
    """Calibrate the target robot's currently held tool for probing."""

    type: Literal["CALIBRATE_TOOL"] = "CALIBRATE_TOOL"
    schema_version: Literal[1] = 1

    z_only: bool = Field(
        description=(
            "When true, calibrate only for z-axis probing. When false, calibrate x, y, and z."
        )
    )

    persistent: bool = Field(
        default=False,
        description="Whether calibration should persist beyond the current session.",
    )
