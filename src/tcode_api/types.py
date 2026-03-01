"""Shared types used across TCode API schemas."""

from typing import Annotated

from pydantic import Field

UnsanitizedFloat = Annotated[
    float | int | str,
    Field(
        description=(
            "A float value that has not yet been sanitized. ",
            "Can be a float, int, or string representation of a number.",
        ),
    ),
]

Matrix = Annotated[
    list[list[float]],
    Field(
        description=(
            "A 3D 4x4 transformation matrix represented in row-major order. ",
            "Used to represent the position and orientation in 3D space.",
        ),
    ),
]


def identity_transform() -> Matrix:
    """Generate an identity transform matrix."""
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


CommandID = str  # Identifier specifically for TCode command
