from typing import Annotated

from pydantic import Field

from .acquire_locks.latest import ACQUIRE_LOCKS
from .release_locks.latest import RELEASE_LOCKS
from .jog_cartesian.latest import JOG_CARTESIAN

RTMessage = Annotated[
    ACQUIRE_LOCKS | RELEASE_LOCKS | JOG_CARTESIAN,
    Field(discriminator="type", description="Union type of all valid real-time messages."),
]
