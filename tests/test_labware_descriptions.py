"""Verify that labware_descriptions stored as json in tcode_api/data are all valid."""

import json
import pathlib
import unittest
from typing import get_args

import plac  # type: ignore[import-untyped]

import tcode_api.api as tc
from tcode_api.utilities import load_labware

labware_json_dir = pathlib.Path(__file__).parent.parent / "tcode_labware"


# Goal: Create a mapping of `type` string to the corresponding description|descriptor constructor
# This way we can grab the `type` field from a json blob and construct the corresponding object.
#
# Labware constructors are dynamically loaded from the type annotations of the LabwareDescriptor and LabwareDescription discriminated unions, so this mapping will automatically be updated as new labware types are added.
# Source for that specific garbage: https://stackoverflow.com/a/64643971
descriptor_constructor_map: dict[
    str, type[tc.LabwareDescriptor | tc.PipetteTipDescriptor | tc.TubeDescriptor]
] = {}
_descriptor_endpoints = list(get_args(get_args(tc.LabwareDescriptor)[0])) + [
    tc.PipetteTipDescriptor,
    tc.TubeDescriptor,
]
for endpoint in _descriptor_endpoints:
    descriptor_constructor_map[endpoint.model_fields["type"].default] = endpoint

description_constructor_map: dict[
    str, type[tc.LabwareDescription | tc.PipetteTipDescription | tc.TubeDescription]
] = {}
_description_endpoints = list(get_args(get_args(tc.LabwareDescription)[0])) + [
    tc.PipetteTipDescription,
    tc.TubeDescription,
]
for endpoint in _description_endpoints:
    description_constructor_map[endpoint.model_fields["type"].default] = endpoint


class TestLabware(unittest.TestCase):
    """Test that all labware json files are valid as descriptions and descriptors."""

    def _read_data_from_file(self, filepath: pathlib.Path) -> dict:
        """Read JSON data from a file and return it as a dictionary."""
        with filepath.open("r") as f:
            try:
                content = f.read()
            except UnicodeDecodeError as err:
                raise AssertionError(
                    f"File {filepath} is not a valid UTF-8 encoded JSON file"
                ) from err

        try:
            content_json = json.loads(content)
        except json.JSONDecodeError as err:
            raise AssertionError(f"File {filepath} does not contain valid JSON") from err

        return content_json

    def load_labware_descriptor(self, filepath: pathlib.Path) -> None:
        """Test that labware description stored in file is a valid LabwareDescription."""
        self._load_labware(filepath, descriptor_constructor_map)

    def load_labware_description(self, filepath: pathlib.Path) -> None:
        """Test that labware description stored in file is a valid LabwareDescriptor."""
        self._load_labware(filepath, description_constructor_map)

    def _load_labware(self, filepath: pathlib.Path, constructor_map: dict[str, type]) -> None:
        """Test that labware description stored in file is registered in given constructor_map and
        can be deserialized."""
        content_json = self._read_data_from_file(filepath)
        try:
            constructor = constructor_map[content_json["type"]]
        except KeyError as e:
            raise ValueError(
                f"type '{content_json['type']}' not registered with test harness: options={list(constructor_map.keys())}"
            ) from e

        constructor(**content_json)

    def test_labware_files(self) -> None:
        """Test that all labware json files are valid."""
        self.assertTrue(labware_json_dir.exists(), f"{labware_json_dir} does not exist")
        for file in labware_json_dir.iterdir():
            with self.subTest(file=file):
                self.load_labware_description(file)
                self.load_labware_descriptor(file)
        load_labware("3d_printed_trash_can")


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
