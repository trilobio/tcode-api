"""tcode_api.api.commands unittests."""

import datetime
import logging
import unittest
from typing import get_args

# Using the below import style because it's how we expect users to import tcode_api
import tcode_api.api as tc
from tcode_api.api.commands import _RobotSpecificTCodeBase, _TCodeBase

from .test_core import BaseTestCases


class TestTCodeScript(BaseTestCases.TestConfiguredBaseModel):
    """TCodeScript class unittests."""

    model = tc.TCodeScript

    def _create_valid_model_instance(self) -> tc.TCodeScript:
        """Create a valid TCodeScript instance for testing."""
        return tc.TCodeScript(
            metadata=tc.Metadata(
                name="unittest",
                timestamp=datetime.datetime.now().isoformat(),
                tcode_api_version="0.1.0",
            ),
        )

    def test_instantiate_tcodescript(self) -> None:
        """Ensure that TCodeScript can be instantiated."""
        model = self._create_valid_model_instance()
        self.assertEqual(len(model.commands), 0)

    def test_file_io(self) -> None:
        """Suppress logging during file I/O test."""
        try:
            original_level = logging.getLogger("tcode_api.api.commands").level
            logging.getLogger("tcode_api.api.commands").setLevel(logging.ERROR)
            super().test_file_io()
        finally:
            logging.getLogger("tcode_api.api.commands").setLevel(original_level)


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
