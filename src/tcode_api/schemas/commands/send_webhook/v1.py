from typing import Literal

from pydantic import Field

from ..base import BaseTCodeCommand


class SEND_WEBHOOK_V1(BaseTCodeCommand):
    """Send an HTTP webhook request."""

    type: Literal["SEND_WEBHOOK"] = "SEND_WEBHOOK"
    schema_version: Literal[1] = 1

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
