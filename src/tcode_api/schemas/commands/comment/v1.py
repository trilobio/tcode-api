from typing import Literal

from pydantic import Field

from ..base.tcode_command.v1 import BaseTCodeCommandV1


class COMMENT(BaseTCodeCommandV1):
    """A human-readable comment in the TCode script."""

    type: Literal["COMMENT"] = "COMMENT"
    schema_version: Literal[1] = 1

    text: str = Field(description="The comment text.")
