"""Verify that labware_descriptions stored as json in tcode_api/data are all valid."""

import json
import pathlib
import unittest
import plac  # type: ignore[import-untpyed]
import tcode_api.api as tc


labware_json_dir = pathlib.Path(__file__).parent.parent / "data"


class TestLabwareDescriptions(unittest.TestCase):
    """Test that all labware descriptions are valid."""

    def load_labware_description(self, filepath: pathlib.Path) -> None:
        """Test that all labware descriptions are valid."""
        with filepath.open("r") as f:
            content = f.read()

        content_json = json.loads(content)
        match content_json["type"]:
            case "WellPlate":
                constructor = tc.WellPlateDescription
            case "TipRack":
                constructor = tc.TipRackDescription
            case "Trash":
                constructor = tc.TrashDescription
            case "Lid":
                constructor = tc.LidDescription
            case _:
                raise ValueError(f"Unknown labware type: {content_json['type']}")

        constructor(**content_json)

    def test_labware_descriptions(self) -> None:
        """Test that all labware descriptions are valid."""
        self.assertTrue(labware_json_dir.exists(), f"{labware_json_dir} does not exist")
        for file in labware_json_dir.iterdir():
            with self.subTest(file=file):
                self.load_labware_description(file)


@plac.annotations(
    labware_filepath=("Path to a single labware description JSON file", "positional", None, pathlib.Path)
)
def main(labware_filepath: pathlib.Path) -> None:
    """Run test_labware_descriptions for a single labware."""
    test_class = TestLabwareDescriptions()
    test_class.load_labware_description(labware_filepath)


if __name__ == "__main__":
    plac.call(main)
