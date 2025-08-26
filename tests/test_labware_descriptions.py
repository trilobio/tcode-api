"""Verify that labware_descriptions stored as json in tcode_api/data are all valid."""

import json
import pathlib
import unittest
from typing import get_args

import plac  # type: ignore[import-untyped]

import tcode_api.api as tc

labware_json_dir = pathlib.Path(__file__).parent.parent / "data"


# https://stackoverflow.com/a/64643971
descriptor_constructor_map: dict[str, type[tc.LabwareDescriptor]] = {}
for endpoint in get_args(get_args(tc.LabwareDescriptor)[0]):
    descriptor_constructor_map[endpoint.__fields__["type"].default] = endpoint

description_constructor_map: dict[str, type[tc.LabwareDescription]] = {}
for endpoint in get_args(get_args(tc.LabwareDescription)[0]):
    description_constructor_map[endpoint.__fields__["type"].default] = endpoint


class TestLabware(unittest.TestCase):
    """Test that all labware json files are valid as descriptions and descriptors."""

    def load_labware_descriptor(self, filepath: pathlib.Path) -> None:
        """Test that labware description stored in file is a valid LabwareDescription."""
        with filepath.open("r") as f:
            content = f.read()

        content_json = json.loads(content)
        try:
            constructor = descriptor_constructor_map[content_json["type"]]
        except KeyError as e:
            raise ValueError(f"Unknown labware type: {content_json['type']}") from e

        constructor(**content_json)

    def load_labware_description(self, filepath: pathlib.Path) -> None:
        """Test that labware description stored in file is a valid LabwareDescriptor."""
        with filepath.open("r") as f:
            content = f.read()

        content_json = json.loads(content)
        try:
            constructor = description_constructor_map[content_json["type"]]
        except KeyError as e:
            raise ValueError(f"Unknown labware type: {content_json['type']}") from e

        constructor(**content_json)

    def test_labware_files(self) -> None:
        """Test that all labware json files are valid."""
        self.assertTrue(labware_json_dir.exists(), f"{labware_json_dir} does not exist")
        for file in labware_json_dir.iterdir():
            with self.subTest(file=file):
                self.load_labware_description(file)
                self.load_labware_descriptor(file)


@plac.annotations(
    labware_filepath=(
        "Path to a single labware description JSON file",
        "positional",
        None,
        pathlib.Path,
    )
)
def main(labware_filepath: pathlib.Path) -> None:
    """Run test_labware_descriptions for a single labware."""
    test_class = TestLabware()
    test_class.load_labware_description(labware_filepath)
    print("Successfully loaded as LabwareDescription")
    test_class.load_labware_descriptor(labware_filepath)
    print("Successfully loaded as LabwareDescriptor")


if __name__ == "__main__":
    plac.call(main)
