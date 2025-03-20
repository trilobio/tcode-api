"""Unittests for tcode_api.api module."""

import datetime
import unittest

from tcode_api.api import Fleet, Metadata, TCodeAST


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
