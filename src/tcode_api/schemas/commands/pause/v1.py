from typing import Literal

from ..base import BaseRobotSpecificTCodeCommand


class PAUSE_V1(BaseRobotSpecificTCodeCommand):
    """Pause execution of the target robot until manually resumed.

    While ``WAIT`` delays a target robot for a set duration, ``PAUSE`` halts the target robot
    until the user manually resumes execution. To pause the entire fleet, schedule a ``PAUSE``
    for each robot using a ``sync_group`` so they pause together.
    """

    type: Literal["PAUSE"] = "PAUSE"
    schema_version: Literal[1] = 1
