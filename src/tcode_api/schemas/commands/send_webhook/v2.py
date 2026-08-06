"""SEND_WEBHOOK v2

- add robot_id field
"""

from typing import Literal

from pydantic import Field

from ..base.tcode_command.v1 import BaseTCodeCommandV1


class SEND_WEBHOOK(BaseTCodeCommandV1):
    """Send an HTTP webhook request."""

    type: Literal["SEND_WEBHOOK"] = "SEND_WEBHOOK"
    schema_version: Literal[2] = 2

    robot_id: str | None = Field(
        default=None,
        description=(
            "Identifier of the robot whose queue executes this webhook, "
            "previously defined with the ADD_ROBOT command. Optional on the "
            "wire so v1 payloads migrate, but required to schedule — the "
            "engine rejects a SEND_WEBHOOK without a robot_id."
        ),
    )

    pause_execution: bool = Field(description="Whether to pause script execution after sending.")

    ignore_external_error: bool = Field(
        default=False,
        description="Whether to ignore errors from the destination server.",
    )

    url: str = Field(description="Destination URL including protocol.")

    payload: str | None = Field(
        default=None,
        description="Optional JSON payload (max 32 KiB).",
    )
