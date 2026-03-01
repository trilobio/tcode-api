from typing import Literal

from pydantic import Field

from ..base import BaseTCodeCommand


class COMMENT_V1(BaseTCodeCommand):
    """A human-readable comment in the TCode script."""

    type: Literal["COMMENT"] = "COMMENT"
    schema_version: Literal[1] = 1

    text: str = Field(description="The comment text.")
