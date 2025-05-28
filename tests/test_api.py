"""Unittests for tcode_api.api module."""

import datetime
import unittest
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


class TestTCodeEndpoints(unittest.TestCase):
    """Mypy-compliant testing to make sure that all endpoints are included in type."""

    def test_endpoints(self) -> None:
        """Test that all endpoints are included in the type."""
        endpoints = [
            obj
            for obj in tc.__dict__.values()
            if hasattr(obj, "__bases__") and tc._TCodeBase in obj.__bases__
        ]
        # https://stackoverflow.com/a/64643971
        type_options = get_args(get_args(tc.TCode)[0])
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                self.assertIn(
                    endpoint,
                    type_options,
                    f"\n\nACTION ITEM: Add {endpoint} to tcode_api.api.TCode type",
                )


if __name__ == "__main__":
    unittest.main()
