"""Client for scheduling, executing, and clearing TCode from a fleet."""

import logging

import requests

import tcode_api.api as tc
from tcode_api.servicer.servicer_api import (
    GetStatusResponse,
    ScheduleCommandRequest,
    ScheduleCommandResponse,
)

_logger = logging.getLogger(__name__)


class TCodeServicerClient:
    """Simple requests-based client for a TCode servicer."""

    def __init__(self, servicer_url: str) -> None:
        self.servicer_url = servicer_url
        self.timeout = 15  # Reference: https://docs.python-requests.org/en/latest/user/advanced/#timeouts
        # Slightly higher in case you need to detect a robot

    def clear_schedule(self) -> None:
        rsp = requests.delete(f"{self.servicer_url}/schedule", timeout=self.timeout)
        rsp.raise_for_status()

    def clear_tcode_resolution(self) -> None:
        rsp = requests.delete(
            f"{self.servicer_url}/tcode_resolution", timeout=self.timeout
        )
        rsp.raise_for_status()

    def clear_labware(self) -> None:
        rsp = requests.delete(f"{self.servicer_url}/deck", timeout=self.timeout)
        rsp.raise_for_status()

    def dump_tf_tree(self) -> None:
        rsp = requests.post(f"{self.servicer_url}/dump_tf_tree", timeout=self.timeout)
        rsp.raise_for_status()

    def get_status(self) -> GetStatusResponse:
        rsp = requests.get(f"{self.servicer_url}/status", timeout=self.timeout)
        rsp.raise_for_status()
        return GetStatusResponse.model_validate_json(rsp.text)

    def schedule_command(self, id: str, command: tc.TCode) -> ScheduleCommandResponse:
        rsp = requests.post(
            f"{self.servicer_url}/schedule_command",
            json=ScheduleCommandRequest(command_id=id, command=command).model_dump(),
            timeout=self.timeout,
        )
        if requests.codes.ok != rsp.status_code:
            breakpoint()
            _logger.debug("command: %s", command)
            _logger.debug("response: %s", rsp.text)
        rsp.raise_for_status()
        return ScheduleCommandResponse.model_validate_json(rsp.text)

    def schedule_commands(
        self, commands: list[tuple[str, tc.TCode]]
    ) -> list[ScheduleCommandResponse]:
        data = [(id, command.model_dump()) for id, command in commands]
        rsp = requests.put(
            f"{self.servicer_url}/schedule_commands",
            json=data,
            timeout=self.timeout,
        )
        rsp.raise_for_status()
        return [
            ScheduleCommandResponse.model_validate(rsp_dict) for rsp_dict in rsp.json()
        ]

    def set_run_state(self, state: bool) -> None:
        rsp = requests.put(
            f"{self.servicer_url}/run_state",
            params={"state": state},
            timeout=self.timeout,
        )
        rsp.raise_for_status()

    def discover_fleet(self) -> None:
        rsp = requests.get(f"{self.servicer_url}/discover_fleet", timeout=self.timeout)
        rsp.raise_for_status()
