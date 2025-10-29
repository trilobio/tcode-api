"""tcode_api.api.location unittests."""

import unittest

# Using the below import style because it's how we expect users to import tcode_api
import tcode_api.api as tc
from tcode_api.utilities import generate_id


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
