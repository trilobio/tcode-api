"""Unittest the tcode-api utilities."""

import unittest
from collections import namedtuple
from typing import Any, Callable

import tcode_api.api as tc
from tcode_api.utilities import (
    describe_pipette_tip_1x1,
    describe_pipette_tip_1x8,
    describe_pipette_tip_box,
    describe_pipette_tip_group,
    describe_tool_descriptor,
    describe_well_plate,
    format_table,
    well_address_to_index,
)


class TestDescribeEntityFunctions(unittest.TestCase):
    """Test the various describe_*** functions."""

    def _test_describe_entity_function(self, target_function: Callable, target_description) -> None:
        """Verify that the default values returned by describe_pipette_tip_box compile."""
        required_field_names = [
            name for name, info in target_description.model_fields.items() if info.is_required
        ]
        retval = target_function()

        # Check that all required fields are present in the returned descriptor
        for field_name in required_field_names:
            self.assertTrue(
                hasattr(retval, field_name),
                f"{target_function.__name__}() return value missing field required by {target_description.__name__}: {field_name}",
            )

        # Check that the returned descriptor has no unexpected fields
        for field_name in retval.__class__.model_fields.keys():
            self.assertIn(
                field_name,
                target_description.model_fields.keys(),
                f"{target_function.__name__}() return value has unexpected field not defined in {target_description.__name__}: {field_name}",
            )

    def test_describe_entity_functions(self) -> None:
        """Test all the describe_*** functions."""
        Test = namedtuple("Test", ["function", "description"])
        tests = [
            Test(describe_well_plate, tc.WellPlateDescription),
            Test(describe_pipette_tip_group, tc.PipetteTipGroupDescriptor),
            Test(describe_pipette_tip_box, tc.PipetteTipBoxDescription),
            Test(describe_pipette_tip_1x1, tc.PipetteTipGroupDescriptor),
            Test(describe_pipette_tip_1x8, tc.PipetteTipGroupDescriptor),
        ]
        for test in tests:
            with self.subTest(
                function=test.function.__name__, description=test.description.__name__
            ):
                self._test_describe_entity_function(test.function, test.description)

    def test_describe_well_plate_regression(self) -> None:
        """Adding supports_lid arg to describe_well_plate should not break existing code."""
        plate_with_lid = describe_well_plate(has_lid=True)
        assert plate_with_lid.liddability is not None  # mypy type narrowing
        self.assertTrue(plate_with_lid.liddability.supports_lid)
        self.assertIsNotNone(plate_with_lid.liddability.lid)

        plate_without_lid = describe_well_plate()
        assert plate_without_lid.liddability is not None  # mypy type narrowing
        self.assertFalse(plate_without_lid.liddability.supports_lid)
        self.assertIsNone(plate_without_lid.liddability.lid)


class TestWellAddressToIndex(unittest.TestCase):
    """Test the well_address_to_index utility function."""

    def test_standard_plate(self) -> None:
        """Test that well_address_to_index works for a 96-well plate by default."""

        # Test a few sample addresses
        passing_tests = {
            "A1": 0,
            "A2": 1,
            "B1": 12,
            "B2": 13,
            "H1": 84,
            "H12": 95,
        }
        for address, expected_index in passing_tests.items():
            with self.subTest(address=address):
                index = well_address_to_index(address)
                self.assertEqual(
                    index,
                    expected_index,
                    f"Expected {address} to map to index {expected_index}, got {index}",
                )

        # Test some invalid addresses
        failing_tests: list[tuple[Any, type[Exception]]] = [
            ("A0", ValueError),
            ("H13", ValueError),
            ("I1", ValueError),
            ("H0", ValueError),
            ("1A", ValueError),
            ("A", ValueError),
            ("1", ValueError),
            (1, TypeError),
            (b"A1", TypeError),
        ]
        for address, expected_exception in failing_tests:
            with self.subTest(address=address):
                with self.assertRaises(expected_exception):
                    well_address_to_index(address)


class TestDescribeToolDescriptor(unittest.TestCase):
    """Test describe_tool_descriptor labels."""

    def test_pipettes_render_channel_count_and_volume(self) -> None:
        """Pipettes render as C<channel_count>P<max_volume_ul>, converting units as needed."""
        self.assertEqual(
            describe_tool_descriptor(
                tc.SingleChannelPipetteDescriptor(
                    max_volume=tc.ValueWithUnits(magnitude=1000, units="ul")
                )
            ),
            "C1P1000",
        )
        self.assertEqual(
            describe_tool_descriptor(
                tc.EightChannelPipetteDescriptor(
                    max_volume=tc.ValueWithUnits(magnitude=0.2, units="mL")
                )
            ),
            "C8P200",
        )

    def test_pipette_without_max_volume(self) -> None:
        """A pipette with no max_volume renders '?' rather than raising."""
        self.assertEqual(describe_tool_descriptor(tc.SingleChannelPipetteDescriptor()), "C1P?")

    def test_non_pipettes_render_their_type(self) -> None:
        """Probes and grippers render as their type name."""
        self.assertEqual(describe_tool_descriptor(tc.ProbeDescriptor()), "Probe")
        self.assertEqual(describe_tool_descriptor(tc.GripperDescriptor()), "Gripper")


class TestFormatTable(unittest.TestCase):
    """Test the format_table renderer."""

    def test_columns_are_uniform(self) -> None:
        """Every cell in a column is padded to the width of that column's widest entry."""
        rendered = format_table(["A", "Bee"], [["long value", "x"], ["y", "z"]], indent="")
        self.assertEqual(
            rendered.splitlines(),
            [
                "A          | Bee",
                "-----------+----",
                "long value | x",
                "y          | z",
            ],
        )

    def test_short_rows_are_padded(self) -> None:
        """A row with fewer cells than headers is padded rather than raising."""
        rendered = format_table(["A", "B"], [["only"]], indent="")
        self.assertEqual(rendered.splitlines()[-1], "only")

    def test_no_rows_renders_header_only(self) -> None:
        """An empty row list still renders the header and rule."""
        rendered = format_table(["A", "B"], [], indent="")
        self.assertEqual(rendered.splitlines(), ["A | B", "--+--"])
