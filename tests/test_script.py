"""Unittests for tcode_api.script module."""

import pathlib
import tempfile
import unittest

from tcode_api.api import (
    ASPIRATE,
    DISPENSE,
    GET_TIP,
    GET_TOOL,
    Labware,
    Location,
    LocationType,
    Robot,
    SingleChannelPipette,
    ValueWithUnits,
)
from tcode_api.script import TCodeScriptBuilder


class TestTCodeScriptBuilder(unittest.TestCase):

    def test_to_and_from_file(self) -> None:
        """Check that TCodeScripts read and write from file without modification."""
        tip_box = Labware(rows=8, columns=12, serial="tip_box_1")
        well_plate = Labware(rows=8, columns=12, serial="well_plate_1")
        builder = TCodeScriptBuilder(name="unittest_script")
        builder.add_robot(Robot())
        builder.add_tool("pipette", 0, SingleChannelPipette())
        builder.add_labware("tip_box", tip_box)
        builder.add_labware("well_plate", well_plate)
        builder.get_tool("pipette")
        builder.add_command(
            GET_TIP(
                location=Location(
                    type=LocationType.LABWARE_INDEX, data=("tip_box_1", 1)
                )
            )
        )
        builder.get_tip("tip_box", 0)
        builder.goto_labware_index("well_plate", 0)  # Well A1
        builder.aspirate(100.0)
        builder.goto_labware_index("well_plate", 1)  # Well A2
        builder.dispense(100.0)
        builder.drop_tip("tip_box", 0)
        builder.drop_tool()
        ast = builder.emit()

        with tempfile.NamedTemporaryFile(delete=True, suffix=".tc") as temp_file:
            # Write to temporary file
            file_path = pathlib.Path(temp_file.name)
            builder.write_to_file(file_path, overwrite=True)

            # Read from temporary file
            builder.set_up_from_file(file_path)

        new_ast = builder.emit()

        # Check that the ASTs are equal
        self.assertEqual(ast, new_ast)

    def test_from_file(self) -> None:
        file = pathlib.Path("~/Workspace/trilobio/aceta/tcode/data/basic_fluid_move.tc")
        builder = TCodeScriptBuilder(name=file.name)
        builder.set_up_from_file(file.expanduser())
        pass


if __name__ == "__main__":
    unittest.main()
