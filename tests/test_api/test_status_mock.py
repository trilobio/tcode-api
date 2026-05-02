"""Tests for `GetStatusResponse.mock` (chunk 7.1)."""

import unittest

from tcode_api.servicer.servicer_api import GetStatusResponse, Result


def _ok_result() -> Result:
    """Minimal `Result` for response construction; payload shape isn't relevant here."""
    return Result(success=True, code="", error_message="", details={})


class TestGetStatusResponseMockField(unittest.TestCase):
    def test_mock_defaults_false(self) -> None:
        """`mock` defaults to False so older servers/payloads round-trip as live."""
        response = GetStatusResponse(
            command_id=None,
            operation_count=0,
            run_state=False,
            result=_ok_result(),
        )
        self.assertFalse(response.mock)

    def test_mock_round_trips_true(self) -> None:
        response = GetStatusResponse(
            command_id=None,
            operation_count=0,
            run_state=False,
            result=_ok_result(),
            mock=True,
        )
        round_tripped = GetStatusResponse.model_validate_json(response.model_dump_json())
        self.assertTrue(round_tripped.mock)

    def test_legacy_payload_without_mock_key(self) -> None:
        """A pre-7.1 server payload (no `mock` key) still validates as `mock=False`."""
        legacy = {
            "command_id": None,
            "operation_count": 0,
            "run_state": False,
            "result": {"success": True, "code": "", "error_message": "", "details": {}},
            "robots": [],
        }
        response = GetStatusResponse.model_validate(legacy)
        self.assertFalse(response.mock)


if __name__ == "__main__":
    unittest.main()
