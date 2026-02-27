from typing import Literal, Self

from pydantic import Field

from ..base import BaseSchemaVersionedModel


class PipetteTipLayoutV1(BaseSchemaVersionedModel):
    """Data structure representing the layout of pipette tips in a box.

    :note: This class is designed to allow non-standard use cases, like adding partially filled
        pipette tip boxes to the deck with the :class:``ADD_LABWARE`` command.
    """

    type: Literal["PipetteTipLayout"] = "PipetteTipLayout"
    schema_version: Literal[1] = 1

    layout: list[list[int]] = Field(
        description=(
            "A 2D list representing the layout of pipette tips in the box. "
            "The list contains either 0 or 1, "
            "where 1 represents a slot holding a pipette tip "
            "and 0 represents an empty slot."
        ),
    )

    @classmethod
    def empty(cls, row_count: int = 8, column_count: int = 12) -> Self:
        """Create a layout with no pipette tips.

        :param row_count: The number of rows in the pipette tip box (default: 8).
        :param column_count: The number of columns in the pipette tip box (default: 12).

        :return: A PipetteTipLayout with all slots empty (0).
        """
        return cls(layout=[[0 for _ in range(column_count)] for _ in range(row_count)])

    @classmethod
    def full(cls, row_count: int = 8, column_count: int = 12) -> Self:
        """Create a layout with all pipette tips filled.

        :param row_count: The number of rows in the pipette tip box (default: 8).
        :param column_count: The number of columns in the pipette tip box (default: 12).

        :return: A PipetteTipLayout with all slots filled (1).
        """
        return cls(layout=[[1 for _ in range(column_count)] for _ in range(row_count)])
