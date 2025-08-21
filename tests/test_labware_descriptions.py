"""Verify that labware_descriptions stored as json in tcode_api/data are all valid."""

import json
import pathlib
import unittest
import plac  # type: ignore[import-untpyed]
import tcode_api.api as tc


labware_json_dir = pathlib.Path(__file__).parent.parent / "data"


class TestLabwareDescriptions(unittest.TestCase):
    """Test that all labware descriptions are valid."""

    def load_labware_descriptor(self, filepath: pathlib.Path) -> None:
        """Test that labware description stored in file is a valid LabwareDescription."""
        with filepath.open("r") as f:
            content = f.read()
        well_plate_type = tc.WellPlateDescriptor().type
        pipette_tip_rack_typew = tc.PipetteTipRackDescriptor().type

        content_json = json.loads(content)
        match content_json["type"]:
            case tc.WellPlateDescription.type:
                constructor = tc.WellPlateDescription
            case tc.TipRackDescription.type:
                constructor = tc.TipRackDescription
            case tc.TubeHolderDescription.type:
                constructor = tc.TubeHolderDescription
            case "Trash":
                constructor = tc.TrashDescription
            case "Lid":
                constructor = tc.LidDescription
            case _:
                raise ValueError(f"Unknown labware type: {content_json['type']}")

        constructor(**content_json)

    def load_labware_description(self, filepath: pathlib.Path) -> None:
        """Test that labware description stored in file is a valid LabwareDescriptor."""
        with filepath.open("r") as f:
            content = f.read()

        content_json = json.loads(content)
        match content_json["type"]:
            case "WellPlate":
                constructor = tc.WellPlateDescriptor
            case "TipRack":
                constructor = tc.TipRackDescriptor
            case "Trash":
                constructor = tc.TrashDescriptor
            case "Lid":
                constructor = tc.LidDescriptor
            case _:
                raise ValueError(f"Unknown labware type: {content_json['type']}")

        constructor(**content_json)

    def test_labware_files(self) -> None:
        """Test that all labware json files are valid."""
        self.assertTrue(labware_json_dir.exists(), f"{labware_json_dir} does not exist")
        for file in labware_json_dir.iterdir():
            with self.subTest(file=file):
                self.load_labware_description(file)
                self.load_labware_descriptor(file)


@plac.annotations(
    labware_filepath=("Path to a single labware description JSON file", "positional", None, pathlib.Path)
)
def main(labware_filepath: pathlib.Path) -> None:
    """Run test_labware_descriptions for a single labware."""
    test_class = TestLabwareDescriptions()
    test_class.load_labware_description(labware_filepath)
    print("Successfully loaded as LabwareDescription")
    test_class.load_labware_descriptor(labware_filepath)
    print("Successfully loaded as LabwareDescriptor")


if __name__ == "__main__":
    plac.call(main)
