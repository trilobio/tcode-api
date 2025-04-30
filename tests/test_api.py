"""Unittests for tcode_api.api module."""

import datetime
import unittest
import warnings
from typing import get_args

import tcode_api.api as tc
from tcode_api.api import _EnumWithDisplayName


class TestEnumWithDisplayName(unittest.TestCase):
    """EnumWithDisplayName unittests."""

    class FruitType(_EnumWithDisplayName):
        """EnumWithDisplayName subclass, referenced in unittests."""

        APPLE = (1, "Apple")
        BANANA = (2, "Banana")
        CHERRY = (3, "Cherry")

    def test_from_value(self) -> None:
        """Test from_value method on an EnumWithDisplayName subclass."""
        with self.subTest("Good integer keys"):
            self.assertEqual(self.FruitType.from_value(1), self.FruitType.APPLE)
            self.assertEqual(self.FruitType.from_value(2), self.FruitType.BANANA)
            self.assertEqual(self.FruitType.from_value(3), self.FruitType.CHERRY)

        with self.subTest("Good string keys"):
            self.assertEqual(self.FruitType.from_value("Apple"), self.FruitType.APPLE)
            self.assertEqual(self.FruitType.from_value("Banana"), self.FruitType.BANANA)
            self.assertEqual(self.FruitType.from_value("Cherry"), self.FruitType.CHERRY)

        with self.subTest("Bad integer keys"):
            self.assertRaises(ValueError, self.FruitType.from_value, 4)

        with self.subTest("Bad string keys"):
            self.assertRaises(ValueError, self.FruitType.from_value, "PEAR")

        with self.subTest("Non-string and non-integer keys"):
            self.assertRaises(TypeError, self.FruitType.from_value, [1])


class TestAPI(unittest.TestCase):

    def test_tcodeast(self) -> None:
        """Ensure that TCodeAST can be instantiated."""
        ast = tc.TCodeAST(
            metadata=tc.Metadata(
                name="unittest_instantiate",
                timestamp=datetime.datetime.now().isoformat(),
                tcode_api_version="0.1.0",
            ),
            fleet=tc.Fleet(),
            tcode=[],
        )
        self.assertEqual(len(ast.tcode), 0)

    def test_serialize(self) -> None:
        """Test TCodeAST is serializable with all possible commands."""
        ast = tc.TCodeAST(
            metadata=tc.Metadata(
                name="unittest_serialize",
                timestamp=datetime.datetime.now().isoformat(),
                tcode_api_version="0.1.0",
            ),
            fleet=tc.Fleet(),
            tcode=[],
        )

        command_instances_to_test: list[tc.TCode] = [
            tc.ASPIRATE(
                volume=tc.ValueWithUnits(magnitude=0.0, units="uL"),
                speed=tc.ValueWithUnits(magnitude=0.0, units="uL/s"),
            ),
            tc.CALIBRATE_FTS_NOISE_FLOOR(axes="xyz", snr=0.0),
            tc.COMMENTS(text="test comment"),
            tc.DISPENSE(
                volume=tc.ValueWithUnits(magnitude=0.0, units="uL"),
                speed=tc.ValueWithUnits(magnitude=0.0, units="uL/s"),
            ),
            tc.DISCARD_PIPETTE_TIP_GROUP(),
            tc.GOTO(location=tc.LocationAsNodeId(data="test_node_id")),
            tc.PAUSE(),
            tc.PICK_UP_PIPETTE_TIP(
                location=tc.LocationAsLabwareIndex(data=("test_labware_id", 0))
            ),
            tc.PICK_UP_TOOL(location=tc.LocationAsNodeId(data="test_node_id")),
            tc.PROBE(
                location=tc.LocationAsLabwareIndex(data=("test_labware_id", 0)),
                speed_fraction=1.0,
                backoff_distance=tc.ValueWithUnits(magnitude=1.0, units="mm"),
            ),
            tc.PUT_DOWN_PIPETTE_TIP(location=tc.LocationAsNodeId(data="test_node_id")),
            tc.PUT_DOWN_TOOL(location=tc.LocationAsNodeId(data="test_node_id")),
            tc.REMOVE_PLATE_LID(plate_id="test_plate"),
            tc.REPLACE_PLATE_LID(plate_id="test_plate"),
            tc.RESET_FTS(),
            tc.RETRIEVE_PIPETTE_TIP_GROUP(id="test_tip_id"),
            tc.RETRIEVE_TOOL(id="test_tool_id"),
            tc.RETURN_PIPETTE_TIP_GROUP(),
            tc.RETURN_TOOL(),
        ]

        # Check that all command types are tested
        with self.subTest("Check test validity"):
            untested_command_types = []
            for command_type in get_args(get_args(tc.TCode)[0]):
                found_match = False
                for command in command_instances_to_test:
                    if isinstance(command, command_type):
                        found_match = True
                        break

                if not found_match:
                    untested_command_types.append(command_type)

            assert (
                len(untested_command_types) == 0
            ), f"Serialization of commands {untested_command_types} not tested in test_api.py"

        for command in command_instances_to_test:
            with self.subTest(command=command):
                ast.tcode = [command]
                with warnings.catch_warnings(record=True) as w_list:
                    ast.model_dump()
                self.assertEqual(
                    len(w_list), 0, f"warning raised on serializing command {command}"
                )


if __name__ == "__main__":
    unittest.main()
