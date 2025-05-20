"""Unittests for tcode_api.script module."""

import pathlib
import tempfile
import unittest

import tcode_api.api as tc
from tcode_api.error import IdExistsError, IdNotFoundError
from tcode_api.script import TCodeScriptBuilder


class TestTCodeScriptBuilder(unittest.TestCase):

    def test_bad_ids(self) -> None:
        """Verify expected failures on bad tool, labware, and robot ids."""
        builder = TCodeScriptBuilder(name="test_bad_ids")

        r0, t0 = "ID-R0", "ID-T0"
        builder.add_robot(tc.Robot(id=r0))
        builder.add_tool(r0, tc.SingleChannelPipette(id=t0))

        with self.subTest("Duplicate robot id"):
            with self.assertRaises(IdExistsError):
                builder.add_robot(tc.Robot(id=r0))

        with self.subTest("Successful tool retrieval"):
            builder.retrieve_tool(t0)

        with self.subTest("Invalid robot id"):
            with self.assertRaises(IdNotFoundError):
                builder.add_tool("ID-R1", tc.SingleChannelPipette(id="ID-T1"))

        with self.subTest("Duplicate tool id"):
            with self.assertRaises(IdExistsError):
                builder.add_tool(r0, tc.SingleChannelPipette(id=t0))

        with self.subTest("Missing tool id"):
            with self.assertRaises(IdNotFoundError):
                builder.retrieve_tool("ID-T1")

        l0 = "ID-L0"
        labware = tc.WellPlate(
            id=l0,
            row_count=8,
            column_count=12,
            row_pitch=tc.ValueWithUnits(magnitude=9.0, units="mm"),
            column_pitch=tc.ValueWithUnits(magnitude=9.0, units="mm"),
            has_lid=False,
        )
        builder.add_labware(labware)
        with self.subTest("Duplicate labware id"):
            with self.assertRaises(IdExistsError):
                builder.add_labware(labware)

        with self.subTest("Successful labware location generation"):
            builder.goto_labware_index(l0, 0)

        with self.subTest("Missing labware id"):
            with self.assertRaises(IdNotFoundError):
                builder.goto_labware_index("ID-L1", 0)

    def test_to_and_from_file(self) -> None:
        """Check that TCodeScripts read and write from file without modification."""
        r0, t0, l0, l1 = "ID-R0", "ID-T0", "ID-L0", "ID-L1"
        tip_box = tc.PipetteTipRack(
            id=l0,
            row_count=8,
            column_count=12,
            row_pitch=tc.ValueWithUnits(magnitude=9.0, units="mm"),
            column_pitch=tc.ValueWithUnits(magnitude=9.0, units="mm"),
            full=True,
            has_lid=False,
        )
        well_plate = tc.WellPlate(
            id=l1,
            row_count=8,
            column_count=12,
            row_pitch=tc.ValueWithUnits(magnitude=9.0, units="mm"),
            column_pitch=tc.ValueWithUnits(magnitude=9.0, units="mm"),
            has_lid=False,
        )
        builder = TCodeScriptBuilder(name="test_to_and_from_file")
        builder.add_robot(tc.Robot(id=r0))
        builder.add_tool(r0, tc.SingleChannelPipette(id=t0))
        builder.add_labware(tip_box)
        builder.add_labware(well_plate)
        builder.retrieve_tool(t0)
        builder.add_command(
            tc.PICK_UP_PIPETTE_TIP(
                location=tc.LocationAsLabwareIndex(labware_id=l0, location_index=1),
            )
        )
        builder.pick_up_pipette_tip(l0, 0)
        builder.goto_labware_index(l1, 0)  # Well A1
        builder.aspirate(100.0)
        builder.goto_labware_index(l1, 1)  # Well A2
        builder.dispense(100.0)
        builder.put_down_pipette_tip(l0, 0)
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
