"""SEND_WEBHOOK v2

- Target a module rather than the fleet: adds the required `module_id` field.
"""

from typing import Literal

from pydantic import Field

from ..base.tcode_command.v1 import BaseTCodeCommandV1


class SEND_WEBHOOK(BaseTCodeCommandV1):
    """Send an HTTP webhook request from a module's queue.

    ``module_id`` names the module the request is addressed to, registered earlier in the
    protocol by :class:``ADD_MODULE``. The request is ordered against that module's other
    work, and because a module has its own queue, sending a webhook does not occupy a robot.
    To order a webhook against robot motion, use ``depends_on`` or ``sync_group`` on the
    schedule envelope.

    :raises ValidatorError: ``ValidatorErrorCode.ID_NOT_FOUND`` if ``module_id`` was not
        registered by an earlier ``ADD_MODULE``.
    """

    type: Literal["SEND_WEBHOOK"] = "SEND_WEBHOOK"
    schema_version: Literal[2] = 2

    module_id: str = Field(
        description=(
            "TCode ID of the module to send from, "
            "assigned previously by the :class:``ADD_MODULE`` command."
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
