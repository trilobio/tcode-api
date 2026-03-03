"""Unittests for the API migration and compatibility logic."""

import unittest

from tcode_api.api.compat import (
    APIHistoryLog,
    TargetSchemaExistsError,
    TargetSchemaNotFoundError,
    resolve_api_profile,
)

TeaPartyAPIHistoryLog = APIHistoryLog(
    name="tea-party-api",
    increments={
        "v0.1.0": {
            "POUR_TEA": 1,
            "SMASH_CUP": 1,
            "TeaCup": 1,
        },
        "v0.1.1": {
            "POUR_TEA": 2,
            "TeaCup": 2,
        },
        "v0.2.0": {
            "CoffeeCup": 1,
            "POUR_COFFEE": 1,
            "TeaCup": 3,
        },
        "v0.4.0": {
            "SMASH_CUP": None,
        },
    },
    renames={
        "v0.3.0": {
            "POUR_TEA": "POUR",
        }
    },
    replacements={
        "v0.3.0": {
            "POUR_COFFEE": "POUR",
        }
    },
)


class TestResolveAPIProfile(unittest.TestCase):
    """Tests for the ``resolve_api_profile`` function."""

    def _assert_dicts_equal(self, dict1: dict, dict2: dict) -> None:
        """Helper method to assert that two dicts are equal, ignoring order."""
        missing_keys = set(dict1.keys()) - set(dict2.keys())
        extra_keys = set(dict2.keys()) - set(dict1.keys())
        bad_values = {
            key: (dict1[key], dict2[key])
            for key in dict1
            if key in dict2 and dict1[key] != dict2[key]
        }
        if len(missing_keys) > 0 or len(extra_keys) > 0 or len(bad_values) > 0:
            error_message = (
                "Dicts are not equal:\n" "  Dict1: {dict1}\n" "  Dict2: {dict2}\n"
            ).format(dict1=dict1, dict2=dict2)
            if len(missing_keys) > 0:
                error_message += f"  dict2 missing keys: {missing_keys}\n"
            if len(extra_keys) > 0:
                error_message += f"  dict2 has extra keys: {extra_keys}\n"
            if len(bad_values) > 0:
                for key, (value1, value2) in bad_values.items():
                    error_message += (
                        f"  Key '{key}' has different values: dict1={value1}, dict2={value2}\n"
                    )
            self.fail(error_message)

    def test_replacement_without_increments(self) -> None:
        """Test that a version that had a replacement without any increments still resolves correctly."""
        api_history_log = APIHistoryLog(
            name="",
            increments={
                "v0.1.0": {"A": 1, "B": 1, "C": 1},
                "v0.2.0": {"A": 2, "C": 2},
            },
            replacements={
                "v0.1.1": {"B": "A"},
            },
        )

        self._assert_dicts_equal({"A": 2, "C": 2}, resolve_api_profile("v0.2.0", api_history_log))

    def test_rename_without_increment(self) -> None:
        """A version with a rename and no increment should resolve correctly."""
        api_history_log = APIHistoryLog(
            name="test_rename_without_increment",
            increments={
                "v0.1.0": {"A": 1, "B": 1, "C": 1},
                "v0.2.0": {"A": 2, "C": 2},
            },
            renames={
                "v0.1.1": {"B": "D"},
            },
        )

        self._assert_dicts_equal(
            {"A": 2, "C": 2, "D": 1}, resolve_api_profile("v0.2.0", api_history_log)
        )

    def test_increment_after_rename(self) -> None:
        """A schema renamed in a prior version should increment from the pre-renamed version."""
        api_history_log = APIHistoryLog(
            name="test_increment_after_rename",
            increments={
                "v0.1.0": {"A": 1, "B": 1, "C": 1},
                "v0.2.0": {"A": 2, "C": 2},
                "v0.3.0": {"D": 2},
            },
            renames={
                "v0.2.0": {"B": "D"},
            },
        )

        self._assert_dicts_equal(
            {"A": 2, "C": 2, "D": 2}, resolve_api_profile("v0.3.0", api_history_log)
        )

    def test_increment_and_rename(self) -> None:
        """A schema that is incremented and renamed in a single version should show the increment with the new name."""
        api_history_log = APIHistoryLog(
            name="test_increment_after_rename",
            increments={
                "v0.1.0": {"A": 1, "B": 1, "C": 1},
                "v0.2.0": {"A": 2, "B": 2, "C": 2},
            },
            renames={
                "v0.2.0": {"B": "D"},
            },
        )

        self._assert_dicts_equal(
            {"A": 2, "D": 2, "C": 2}, resolve_api_profile("v0.2.0", api_history_log)
        )

    def test_rename_nonexistent(self) -> None:
        """A rename with a non-existent target raises an error."""
        api_history_log = APIHistoryLog(
            name="test_increment_after_rename",
            increments={
                "v0.1.0": {"A": 1, "B": 1, "C": 1},
                "v0.2.0": {"A": 2, "B": 2, "C": 2},
            },
            renames={
                "v0.2.0": {"D": "E"},
            },
        )

        with self.assertRaises(TargetSchemaNotFoundError):
            resolve_api_profile("v0.2.0", api_history_log)

    def test_rename_to_existing(self) -> None:
        """A rename to an existing target raises an error."""
        api_history_log = APIHistoryLog(
            name="test_increment_after_rename",
            increments={
                "v0.1.0": {"A": 1, "B": 1, "C": 1},
                "v0.2.0": {"C": 2},
            },
            renames={
                "v0.2.0": {"B": "A"},
            },
        )

        with self.assertRaises(TargetSchemaExistsError):
            resolve_api_profile("v0.2.0", api_history_log)

    def test_too_early_version(self) -> None:
        """Requesting a version before the first increment should return an empty profile."""
        api_history_log = APIHistoryLog(
            name="test_too_early_version",
            increments={
                "v0.1.0": {"A": 1, "B": 1, "C": 1},
            },
        )
        self._assert_dicts_equal(
            {},
            resolve_api_profile("v0.0.1", api_history_log),
        )

    def test_implied_version(self) -> None:
        """Requesting a version that doesn't exist should resolve to the latest version before it."""
        api_history_log = APIHistoryLog(
            name="test_nonexistent_version",
            increments={
                "v0.1.0": {"A": 1, "B": 1, "C": 1},
                "v0.2.0": {"A": 2, "C": 2},
            },
        )
        self._assert_dicts_equal(
            {"A": 1, "B": 1, "C": 1},
            resolve_api_profile("v0.1.5", api_history_log),
        )
        self._assert_dicts_equal(
            {"A": 2, "B": 1, "C": 2},
            resolve_api_profile("v0.2.5", api_history_log),
        )

    def test_invalid_version(self) -> None:
        """Test that an error is raised when an invalid version string is specified."""
        bad_versions = ["invalid_version", "version_0.1.0"]
        for bad_version in bad_versions:
            with self.subTest(bad_version=bad_version), self.assertRaises(ValueError):
                resolve_api_profile(bad_version, TeaPartyAPIHistoryLog)
