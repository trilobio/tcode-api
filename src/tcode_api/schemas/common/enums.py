"""TCode-specific enumeration values.

These aren't schema-versioned because they are aren't serialized - rather, individual values are serialized.

As such, when you change an enum, make sure to bump the schema-version of all of the objects that reference that enum.
"""

from enum import Enum


class PathType(int, Enum):
    """Options for how the robot should move to a target location."""

    DIRECT = 1
    """Robot moves to the target location directly in jointspace."""

    SAFE = 2
    """Robot moves to the target location via a safe path."""

    SHORTCUT = 3
    """Robot uses DIRECT if it is close to the target, otherwise SAFE."""


class GraspType(str, Enum):
    """Options for how a gripper should grasp a piece of labware."""

    UNSPECIFIED = "UNSPECIFIED"
    """Gripper uses LIFT."""

    LIFT = "LIFT"
    """Gripper lifts labware from the bottom. Only use in LabwareHolders that can support this behavior (e.g. DeckSlots)."""

    PINCH = "PINCH"
    """Gripper pinches labware from the sides. Only use this when your source or destination requires it, less stable!"""


class GripperStateType(int, Enum):
    """Gripper fingers state."""

    OPEN = 1
    """The gripper is fully open."""

    CLOSE = 2
    """The gripper is fully closed."""

    WIDTH = 3
    """Gripper is set to a specific distance between the fingers."""


class TrajectoryType(int, Enum):
    """Options for profiles to use for a robot's joint(s) when moving to a target location."""

    JOINT_SQUARE = 1
    """Robot moves in jointspace with square motor profiles."""

    JOINT_TRAPEZOIDAL = 2
    """Robot moves in joint space with trapezoidal motor profiles."""

    JOINT_LINEAR = 3
    """Robot moves in cartesian space with non-uniform motor profiles."""


class WellPartType(str, Enum):
    """Referenceable parts of a well."""

    TOP = "TOP"
    """The center of a well, co-planar with the top of the labware."""

    BOTTOM = "BOTTOM"
    """The deepest point of a well, as centered on it's opening.

    e.g. a well with a triangular bottom will have a BOTTOM that is NOT at the lowest point.
    """
