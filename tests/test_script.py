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
        builder.add_robot_to_ast(tc.Robot(id=r0))
        builder.add_tool_to_ast(r0, tc.SingleChannelPipette(id=t0))

        with self.subTest("Duplicate robot id"):
            with self.assertRaises(IdExistsError):
                builder.add_robot_to_ast(tc.Robot(id=r0))

        with self.subTest("Successful tool retrieval"):
            builder.retrieve_tool(t0)

        with self.subTest("Invalid robot id"):
            with self.assertRaises(IdNotFoundError):
                builder.add_tool_to_ast("ID-R1", tc.SingleChannelPipette(id="ID-T1"))

        with self.subTest("Duplicate tool id"):
            with self.assertRaises(IdExistsError):
                builder.add_tool_to_ast(r0, tc.SingleChannelPipette(id=t0))

        with self.subTest("Missing tool id"):
            with self.assertRaises(IdNotFoundError):
                builder.retrieve_tool("ID-T1")

        l0 = "ID-L0"
        labware = tc.WellPlateDescriptor(
            id=l0,
            row_count=8,
            column_count=12,
            row_pitch=tc.ValueWithUnits(magnitude=9.0, units="mm"),
            column_pitch=tc.ValueWithUnits(magnitude=9.0, units="mm"),
            has_lid=False,
        )
        builder.add_labware_to_ast(labware)
        with self.subTest("Duplicate labware id"):
            with self.assertRaises(IdExistsError):
                builder.add_labware_to_ast(labware)

        with self.subTest("Successful labware location generation"):
            builder.move_to_location(l0, 0)

        with self.subTest("Missing labware id"):
            with self.assertRaises(IdNotFoundError):
                builder.move_to_location("ID-L1", 0)

    def test_to_and_from_file(self) -> None:
        """Check that TCodeScripts read and write from file without modification."""
        r0, t0, l0, l1 = "ID-R0", "ID-T0", "ID-L0", "ID-L1"
        tip_box = tc.PipetteTipRackDescriptor(
            id=l0,
            row_count=8,
            column_count=12,
            row_pitch=tc.ValueWithUnits(magnitude=9.0, units="mm"),
            column_pitch=tc.ValueWithUnits(magnitude=9.0, units="mm"),
            full=True,
            has_lid=False,
        )
        well_plate = tc.WellPlateDescriptor(
            id=l1,
            row_count=8,
            column_count=12,
            row_pitch=tc.ValueWithUnits(magnitude=9.0, units="mm"),
            column_pitch=tc.ValueWithUnits(magnitude=9.0, units="mm"),
            has_lid=False,
        )
        builder = TCodeScriptBuilder(name="test_to_and_from_file")
        builder.add_robot_to_ast(tc.Robot(id=r0))
        builder.add_tool_to_ast(r0, tc.SingleChannelPipette(id=t0))
        builder.add_labware_to_ast(tip_box)
        builder.add_labware_to_ast(well_plate)
        builder.retrieve_tool(t0)
        builder.add_command(
            tc.PICK_UP_PIPETTE_TIP(
                location=tc.LocationAsLabwareIndex(labware_id=l0, location_index=1),
            )
        )
        builder.pick_up_pipette_tip(l0, 0)
        builder.move_to_location(l1, 0)  # Well A1
        builder.aspirate(100.0)
        builder.move_to_location(l1, 1)  # Well A2
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

    def test_reset(self) -> None:
        """Check that reset() treats the name attribute appropriately."""
        name_a, name_b = "test_reset-a", "test_reset-b"
        desc_a, desc_b = "test_reset-a description", "test_reset-b description"
        builder = TCodeScriptBuilder(name=name_a, description=desc_a)
        ast = builder.emit()
        self.assertEqual(ast.metadata.name, name_a)
        self.assertEqual(ast.metadata.description, desc_a)
        name, desc = None, None
        with self.subTest(name=name, description=desc):
            builder.reset(name=name, description=desc)
            ast = builder.emit()
            self.assertEqual(ast.metadata.name, name_a)
            self.assertEqual(ast.metadata.description, None)

        desc = desc_b
        with self.subTest(name=name, description=desc):
            builder.reset(name=name, description=desc)
            ast = builder.emit()
            self.assertEqual(ast.metadata.name, name_a)
            self.assertEqual(ast.metadata.description, desc_b)

        name, desc = name_b, None
        with self.subTest(name=name, description=desc):
            builder.reset(name=name, description=desc)
            ast = builder.emit()
            self.assertEqual(ast.metadata.name, name_b)
            self.assertEqual(ast.metadata.description, None)

    def test_endpoints_are_implemented(self) -> None:
        """Check that builder has method implemented for each TCode endpoint."""
        endpoints = [
            obj
            for obj in tc.__dict__.values()
            if hasattr(obj, "__bases__") and tc._TCodeBase in obj.__bases__
        ]
        endpoint_names = {
            endpoint.__name__.split(".")[-1].lower() for endpoint in endpoints
        }
        print(endpoint_names)
        for endpoint_name in endpoint_names:
            with self.subTest(endpoint_name=endpoint_name):
                self.assertTrue(
                    hasattr(
                        TCodeScriptBuilder,
                        endpoint_name,
                    ),
                    f"Missing method for endpoint: {endpoint_name}",
                )


if __name__ == "__main__":
    unittest.main()
