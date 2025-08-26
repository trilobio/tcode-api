"""Unittests for tcode_api.api module."""

import datetime
import unittest
from typing import get_args

import tcode_api.api as tc
from tcode_api.utilities import generate_id


class TestAPI(unittest.TestCase):

    def test_tcodeast(self) -> None:
        """Ensure that TCodeScript can be instantiated."""
        script = tc.TCodeScript(
            metadata=tc.Metadata(
                name="unittest_instantiate",
                timestamp=datetime.datetime.now().isoformat(),
                tcode_api_version="0.1.0",
            ),
        )
        self.assertEqual(len(script.commands), 0)

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


class TestLocationAsLabwareIndex(unittest.TestCase):
    """Regression test for verifying that LocationAsLabwareIndex can be
    loaded using FastAPI.

    The fundamental issue (and solution) is outlined here, has to do with pydantic's strict-by-default type coercion:
        https://github.com/pydantic/pydantic/discussions/8726#discussioncomment-10427646

    Update: changed typehint in LocationAsLabwareIndex from WellPartType enum to str as temp fix, but this sucks!
    """

    def test_enum_validation_as_enum_entry(self) -> None:
        """Test that model_validate method works for enum entry."""
        tc.LocationAsLabwareIndex.model_validate(
            {
                "labware_id": generate_id(),
                "location_index": 0,
                "well_part": "TOP",
            },
            strict=True,
        )

    def test_enum_validation_as_str(self) -> None:
        """Test that model_validate method works for string."""
        tc.LocationAsLabwareIndex.model_validate(
            {
                "labware_id": generate_id(),
                "location_index": 0,
                "well_part": tc.WellPartType.BOTTOM,
            },
            strict=True,
        )


class TestTCodeEndpoints(unittest.TestCase):
    """Mypy-compliant testing to make sure that all endpoints are included in type."""

    def test_endpoints(self) -> None:
        """Test that all endpoints are included in the type."""
        ENDPOINTS_TO_SKIP = [tc._RobotSpecificTCodeBase]
        endpoints = [
            obj
            for obj in tc.__dict__.values()
            if hasattr(obj, "__bases__")
            and (
                tc._TCodeBase in obj.__bases__
                or tc._RobotSpecificTCodeBase in obj.__bases__
            )
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


if __name__ == "__main__":
    unittest.main()
