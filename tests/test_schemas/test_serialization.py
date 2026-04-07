"""Test serializing and de-serializing schemas of various veresions."""

import tempfile
import unittest

from tcode_api.schemas.common.value_with_units import ValueWithUnits
from tcode_api.schemas.descriptions.grid.v1 import GridDescription
from tcode_api.schemas.descriptions.labware.pipette_tip_box.v1 import (
    PipetteTipBoxDescription as PipetteTipBoxDescriptionV1,
)
from tcode_api.schemas.descriptions.labware.pipette_tip_box.v2 import (
    PipetteTipBoxDescription as PipetteTipBoxDescriptionV2,
)
from tcode_api.schemas.descriptions.pipette_tip.v1 import PipetteTipDescription


class TestSchemaDeserialization(unittest.TestCase):
    """Test de-serializing schemas of various versions."""

    pipette_tip_box_description = PipetteTipBoxDescriptionV1(
        x_length=ValueWithUnits(magnitude=127.76, units="mm"),
        y_length=ValueWithUnits(magnitude=85.48, units="mm"),
        z_length=ValueWithUnits(magnitude=60.0, units="mm"),
        grid=GridDescription(
            row_count=8,
            column_count=12,
            row_pitch=ValueWithUnits(magnitude=9.0, units="mm"),
            column_pitch=ValueWithUnits(magnitude=9.0, units="mm"),
            row_offset=ValueWithUnits(magnitude=0.0, units="mm"),
            column_offset=ValueWithUnits(magnitude=0.0, units="mm"),
        ),
        pipette_tip=PipetteTipDescription(
            has_filter=False,
            height=ValueWithUnits(magnitude=50.0, units="mm"),
            flange_height=ValueWithUnits(magnitude=10.0, units="mm"),
            max_volume=ValueWithUnits(magnitude=200.0, units="µL"),
            min_volume=ValueWithUnits(magnitude=10.0, units="µL"),
        ),
        full=True,
    )

    def test_labware_serialization_works_on_single_schema_version(self) -> None:
        """PipetteTipBoxDescriptionV1 should serialize and de-serialize to the same description."""
        with tempfile.NamedTemporaryFile(suffix=".json") as temp_file:
            with open(temp_file.name, "w") as f:
                self.pipette_tip_box_description.write(f)

            with open(temp_file.name, "r") as f:
                deserialized_description = PipetteTipBoxDescriptionV1.read(f)

        self.assertEqual(
            deserialized_description,
            self.pipette_tip_box_description,
            "data unexpectedly de-serialized to a different description than the original",
        )

    def test_labware_serialization_errors_on_different_schema_versions(self) -> None:
        """PipetteTipBoxDescriptionV1 should fail to deserialize with PipetteTipBoxDescriptionV2."""
        with tempfile.NamedTemporaryFile(suffix=".json") as temp_file:
            with open(temp_file.name, "w") as f:
                self.pipette_tip_box_description.write(f)

            with (
                open(temp_file.name, "r") as f,
                self.assertRaises(
                    ValueError, msg="data unexpectedly de-serialized with the wrong schema version"
                ),
            ):
                PipetteTipBoxDescriptionV2.read(f)
