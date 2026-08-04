"""PAUSE v2

- Scope to a specific robot (extend `BaseRobotSpecificTCodeCommandV1` instead of
  `BaseTCodeCommandV1`).
"""

from typing import Literal

from ..base.robot_specific_tcode_command.v1 import BaseRobotSpecificTCodeCommandV1


class PAUSE(BaseRobotSpecificTCodeCommandV1):
    """Pause execution of the target robot until manually resumed.

    While ``WAIT`` delays a target robot for a set duration, ``PAUSE`` halts the target robot
    until the user manually resumes execution. To pause the entire fleet, schedule a ``PAUSE``
    for each robot using a ``sync_group`` so they pause together.
    """

    type: Literal["PAUSE"] = "PAUSE"
    schema_version: Literal[2] = 2
