"""tcode_api.api.commands unittests."""

import datetime
import tempfile
import unittest
from typing import get_args

import tcode_api.api as tc
from tcode_api.api.commands import _RobotSpecificTCodeBase, _TCodeBase


class TestTCodeScript(unittest.TestCase):
    """TCodeScript class unittests."""

    def test_instantiate_tcodescript(self) -> None:
        """Ensure that TCodeScript can be instantiated."""
        script = tc.TCodeScript(
            metadata=tc.Metadata(
                name="unittest_instantiate",
                timestamp=datetime.datetime.now().isoformat(),
                tcode_api_version="0.1.0",
            ),
        )
        self.assertEqual(len(script.commands), 0)

    def test_file_io(self) -> None:
        """Test file serialization and deserialization of TCodeScript."""
        script = tc.TCodeScript(
            metadata=tc.Metadata(
                name="unittest_file_io",
                timestamp=datetime.datetime.now().isoformat(),
                tcode_api_version="0.1.0",
            ),
        )
        with tempfile.TemporaryFile(mode="w+") as text_io:
            script.write(text_io)
            text_io.seek(0)
            script_read = tc.TCodeScript.read(text_io)

        self.assertEqual(script, script_read)


class TestAPI(unittest.TestCase):
    """Various unsorted unittests."""

    def test_descriptors(self) -> None:
        """Ensure that LabwareDescriptors can be instantiated without specifying certain attributes."""
        tc.GripperDescriptor()
        tc.LidDescriptor()
        tc.SingleChannelPipetteDescriptor()
        tc.EightChannelPipetteDescriptor()
        tc.PipetteTipBoxDescriptor()
        tc.ProbeDescriptor()
        tc.RobotDescriptor()
        tc.TrashDescriptor()
        tc.WellPlateDescriptor()


class TestTCodeEndpoints(unittest.TestCase):
    """Mypy-compliant testing to make sure that all endpoints are included in type."""

    def test_endpoints(self) -> None:
        """Test that all endpoints are included in the type."""
        ENDPOINTS_TO_SKIP = [_RobotSpecificTCodeBase]
        endpoints = [
            obj
            for obj in tc.__dict__.values()
            if hasattr(obj, "__bases__")
            and (_TCodeBase in obj.__bases__ or _RobotSpecificTCodeBase in obj.__bases__)
        ]
        # https://stackoverflow.com/a/64643971
        type_options = get_args(get_args(tc.TCode)[0])
        for endpoint in endpoints:
            if endpoint in ENDPOINTS_TO_SKIP:
                continue
            with self.subTest(endpoint=endpoint):
                self.assertIn(
                    endpoint,
                    type_options,
                    f"\n\nACTION ITEM: Add {endpoint} to tcode_api.api.TCode type",
                )
