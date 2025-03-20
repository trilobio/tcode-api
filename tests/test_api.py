"""Unittests for tcode_api.api module."""

import datetime
import unittest

from tcode_api.api import EnumWithDisplayName, Fleet, Metadata, TCodeAST


class TestEnumWithDisplayName(unittest.TestCase):
    """EnumWithDisplayName unittests."""

    class FruitType(EnumWithDisplayName):
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
        ast = TCodeAST(
            metadata=Metadata(
                name="unittest_instantiate",
                timestamp=datetime.datetime.now().isoformat(),
                tcode_api_version="0.1.0",
            ),
            fleet=Fleet(),
            tcode=[],
        )
        self.assertEqual(len(ast.tcode), 0)


if __name__ == "__main__":
    unittest.main()
