"""Unittests for tcode_api.script module."""

import pathlib
import tempfile
import unittest

from tcode_api.api import (
    PICK_UP_PIPETTE_TIP,
    Location,
    LocationType,
    PipetteTipRack,
    Robot,
    SingleChannelPipette,
    ValueWithUnits,
    WellPlate,
)
from tcode_api.script import TCodeScriptBuilder


class TestTCodeScriptBuilder(unittest.TestCase):

    def test_bad_keys(self) -> None:
        """Verify expected failures on bad tool and labware keys."""
        builder = TCodeScriptBuilder(name="test_bad_keys")
        builder.add_robot(Robot())
        with self.subTest("Invalid robot index"):
            with self.assertRaises(IndexError):
                builder.add_tool("pipette", 1, SingleChannelPipette())

        builder.add_tool("pipette", 0, SingleChannelPipette())
        with self.subTest("Duplicate tool key"):
            with self.assertRaises(ValueError):
                builder.add_tool("pipette", 0, SingleChannelPipette())

        with self.subTest("Missing tool key"):
            with self.assertRaises(ValueError):
                builder.retrieve_tool("gripper")

        labware = WellPlate(
            id="serial_a",
            row_count=8,
            column_count=12,
            row_pitch=ValueWithUnits(magnitude=9.0, units="mm"),
            column_pitch=ValueWithUnits(magnitude=9.0, units="mm"),
        )
        builder.add_labware("well_plate_1", labware)
        with self.subTest("Duplicate labware serial"):
            with self.assertRaises(ValueError):
                builder.add_labware("well_plate_2", labware)

        with self.subTest("Duplicate labware key"):
            with self.assertRaises(ValueError):
                labware.id = "serial_b"
                builder.add_labware("well_plate_1", labware)

        with self.subTest("Missing labware key"):
            with self.assertRaises(ValueError):
                builder.goto_labware_index("well_plate_2", 0)

    def test_to_and_from_file(self) -> None:
        """Check that TCodeScripts read and write from file without modification."""
        tip_box = PipetteTipRack(
            id="tip_box_1",
            row_count=8,
            column_count=12,
            row_pitch=ValueWithUnits(magnitude=9.0, units="mm"),
            column_pitch=ValueWithUnits(magnitude=9.0, units="mm"),
            full=True,
        )
        well_plate = WellPlate(
            id="well_plate_1",
            row_count=8,
            column_count=12,
            row_pitch=ValueWithUnits(magnitude=9.0, units="mm"),
            column_pitch=ValueWithUnits(magnitude=9.0, units="mm"),
        )
        builder = TCodeScriptBuilder(name="test_to_and_from_file")
        builder.add_robot(Robot())
        builder.add_tool("pipette", 0, SingleChannelPipette())
        builder.add_labware("tip_box", tip_box)
        builder.add_labware("well_plate", well_plate)
        builder.retrieve_tool("pipette")
        builder.add_command(
            PICK_UP_PIPETTE_TIP(
                location=Location(
                    type=LocationType.LABWARE_INDEX, data=("tip_box_1", 1)
                )
            )
        )
        builder.pick_up_pipette_tip("tip_box", 0)
        builder.goto_labware_index("well_plate", 0)  # Well A1
        builder.aspirate(100.0)
        builder.goto_labware_index("well_plate", 1)  # Well A2
        builder.dispense(100.0)
        builder.put_down_pipette_tip("tip_box", 0)
        builder.return_tool()
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


if __name__ == "__main__":
    unittest.main()
