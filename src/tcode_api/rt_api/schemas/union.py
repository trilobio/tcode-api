from typing import Annotated

from pydantic import Field

from .acquire_lock.latest import ACQUIRE_LOCK
from .release_lock.latest import RELEASE_LOCK

RTMessage = Annotated[
    ACQUIRE_LOCK | RELEASE_LOCK,
    Field(discriminator="type", description="Union type of all valid real-time messages."),
]
