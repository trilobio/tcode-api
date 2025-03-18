"""Unittests for tcode_api.api module."""

import unittest

from tcode_api.api import Fleet, TCodeAST


class TestAPI(unittest.TestCase):

    def test_tcodeast(self) -> None:
        """Ensure that TCodeAST can be instantiated."""
        ast = TCodeAST(fleet=Fleet(), tcode=[])
        self.assertEqual(len(ast.tcode), 0)


if __name__ == "__main__":
    unittest.main()
