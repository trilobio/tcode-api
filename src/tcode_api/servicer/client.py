"""Client for scheduling, executing, and clearing TCode from a fleet."""

import logging
import time
from itertools import batched

import requests

import tcode_api.api as tc
from tcode_api.servicer.keyboard_input import get_key
from tcode_api.servicer.servicer_api import (
    ClearScheduleResponse,
    EnterTeachModeRequest,
    ExitTeachModeRequest,
    ExitTeachModeResponse,
    GetStatusResponse,
    ScheduleCommandRequest,
    ScheduleCommandResponse,
)
from tcode_api.types import Matrix
from tcode_api.utilities import generate_id, mm, rad

_logger = logging.getLogger(__name__)

_default_servicer_url = "http://localhost:8002"


class TCodeServicerClient:
    """Python client for a TCode servicer.

    Intended to provide an interface with the Trilobio fleet via a single python class, sufficient
    for interacting with the fleet programmatically.
    """

    def __init__(self, servicer_url: str | None = None) -> None:
        self.servicer_url = servicer_url or _default_servicer_url
        self.timeout = (
            5  # Reference: https://docs.python-requests.org/en/latest/user/advanced/#timeouts
        )

    def clear_schedule(self) -> ClearScheduleResponse:
        """Clear all of the currently scheduled (but as yet unexecuted) TCode commands on the fleet.

        :returns: A summary of what was cleared.
        """
        rsp = requests.delete(f"{self.servicer_url}/schedule", timeout=self.timeout)
        rsp.raise_for_status()
        return ClearScheduleResponse.model_validate_json(rsp.text)

    def clear_tcode_resolution(self) -> None:
        """Clear the mapping of TCode ids to real entities on the fleet.

        :note: This command internally calls ``clear_schedule()``, but NOT ``clear_labware()``.
        :note: This command does not clear the physical labware from the deck, merely their ids.
        """

        rsp = requests.delete(f"{self.servicer_url}/tcode_resolution", timeout=self.timeout)
        rsp.raise_for_status()

    def clear_labware(self) -> None:
        """Delete all of the current labware on the fleet.

        :note: "current labware on the fleet" includes all plates and tips, both on the deck and mounted on robots/pipettes.
        """
        rsp = requests.delete(f"{self.servicer_url}/deck", timeout=self.timeout)
        rsp.raise_for_status()

    def dump_tf_tree(self) -> None:
        """Write the current internal state tree to a file for debugging purposes."""
        rsp = requests.post(f"{self.servicer_url}/dump_tf_tree", timeout=self.timeout)
        rsp.raise_for_status()

    def clear_tf_tree_history(self) -> None:
        """Clear transform-tree mutation history (if the server supports it)."""
        rsp = requests.post(
            f"{self.servicer_url}/tf_tree/clear_history",
            timeout=self.timeout,
        )
        if rsp.status_code == 404:
            _logger.warning(
                "Servicer does not support /tf_tree/clear_history; skipping history clear."
            )
            return
        rsp.raise_for_status()

    def get_status(self) -> GetStatusResponse:
        """Return the current status of the servicer and fleet."""
        rsp = requests.get(f"{self.servicer_url}/status", timeout=self.timeout)
        rsp.raise_for_status()
        return GetStatusResponse.model_validate_json(rsp.text)

    def schedule_command(self, id: str, command: tc.TCode) -> ScheduleCommandResponse:
        """Append a single TCode command to the end of the current schedule and register it with the provided id.

        :param id: A unique identifier for the command. References to this command in future calls will use this id.
        :param command: The TCode command to schedule.

        :returns: A report on the attempted scheduling. See :py:class:`ScheduleCommandResponse` for details.
        """
        rsp = requests.post(
            f"{self.servicer_url}/schedule_command",
            json=ScheduleCommandRequest(command_id=id, command=command).model_dump(),
            timeout=self.timeout,
        )
        if requests.codes.ok != rsp.status_code:
            _logger.debug("command: %s", command)
            _logger.debug("response: %s", rsp.text)
        rsp.raise_for_status()
        return ScheduleCommandResponse.model_validate_json(rsp.text)

    def schedule_commands(
        self, commands: list[tuple[str, tc.TCode]]
    ) -> list[ScheduleCommandResponse]:
        """Calls schedule_command() endpoint for a list of commands sequentially.

        :param commands: A list of tuples of (id, command) to schedule.

        :returns: A list of reports on the attempted scheduling, in the same order as the commands were given. See :py:class:`ScheduleCommandResponse` for details.
        """
        data = [(id, command.model_dump()) for id, command in commands]
        rsp = requests.put(
            f"{self.servicer_url}/schedule_commands",
            json=data,
            timeout=self.timeout,
        )
        rsp.raise_for_status()
        return [ScheduleCommandResponse.model_validate(rsp_dict) for rsp_dict in rsp.json()]

    def set_run_state(self, state: bool) -> None:
        """Pause or start the execution of the current schedule.

        :param state: True to start/resume execution, False to pause.
        """
        rsp = requests.put(
            f"{self.servicer_url}/run_state",
            params={"state": state},
            timeout=self.timeout,
        )
        rsp.raise_for_status()

    def teach_point(self, robot_id: str) -> Matrix:
        """Teach a point for the specified robot.

        :param robot_id: The ID of the robot to teach the point for.
            Use the ADD_ROBOT command to set the robot ID.

        :return: The matrix representing the taught point.
        """
        transform: Matrix | None = None
        try:
            rsp = requests.post(
                f"{self.servicer_url}/enter_teach_mode",
                json=EnterTeachModeRequest(robot_id=robot_id).model_dump(),
                timeout=self.timeout,
            )
            rsp.raise_for_status()
            print("Manual Jog Controls (w|s = up|down)\nw|s|q")
            key_control_loop_running = True
            while key_control_loop_running:
                key = get_key()
                match key:
                    case "w":
                        self.schedule_command(
                            id=generate_id(),
                            command=tc.MOVE_TO_JOINT_POSE(
                                robot_id=robot_id,
                                joint_positions=[rad(0), mm(0.5), rad(0), rad(0)],
                                relative=True,
                            ),
                        )
                        self.set_run_state(True)
                    case "s":
                        self.schedule_command(
                            id=generate_id(),
                            command=tc.MOVE_TO_JOINT_POSE(
                                robot_id=robot_id,
                                joint_positions=[rad(0), mm(-0.5), rad(0), rad(0)],
                                relative=True,
                            ),
                        )
                        self.set_run_state(True)
                    case "esc" | "q":
                        print("Exiting")
                        key_control_loop_running = False
                    case _:
                        print(f"Unrecognized char {key}")
        finally:
            rsp = requests.post(
                f"{self.servicer_url}/exit_teach_mode",
                json=ExitTeachModeRequest(robot_id=robot_id).model_dump(),
            )
            rsp.raise_for_status()
            response = ExitTeachModeResponse.model_validate(rsp.json())
            transform = response.transform

        assert (
            transform is not None
        ), "teach_point() managed to fail calling teach_node endpoint(s) without raising an error?"
        return transform

    def discover_fleet(self) -> None:
        """Scan the fleet for new robots, and update all robot states. Useful if you swapped tools manually as a developer."""
        rsp = requests.get(f"{self.servicer_url}/discover_fleet", timeout=20)
        rsp.raise_for_status()

    def execute_run_loop(self) -> None:
        """Run a blocking loop that monitors the servicer's status and exits when the current
            script is complete or an error occurs.

        :note: This method can be interrupted with <Ctrl-C>, which will clear the robot state
            and exit cleanly.
        """
        self.set_run_state(True)
        while True:
            try:
                time.sleep(0.1)
                status = self.get_status()

                if status.operation_count == 0:
                    self.set_run_state(False)
                    return

                if not status.result.success:
                    msg = f"tcode service hit Runtime error on command(id={status.command_id}): {status.result.message} (see debug logs for stacktrace)"
                    if status.result.details is not None:
                        for line in status.result.details.get("traceback", "").split("\n"):
                            _logger.debug(line)
                    _logger.fatal(msg)
                    self.set_run_state(False)
                    return

            except KeyboardInterrupt:
                self.set_run_state(False)
                self.clear_tcode_resolution()
                self.clear_labware()
                return

    def run_script(self, script: tc.TCodeScript, clean_environment: bool = True, batch_process: bool = False) -> None:
        """Schedule and execute a TCode script on the fleet, starting from an empty state.

        This is a convenience method that combines scheduling, starting execution, and monitoring
        into a single call.

        :param script: The TCode script to run.
        """
        if clean_environment:
            self.clear_schedule()
            self.clear_labware()
            self.clear_tcode_resolution()
            self.clear_tf_tree_history()
            self.discover_fleet()

        total_commands = len(script.commands)

        if not batch_process:
            for i, command in enumerate(script.commands):
                _logger.debug("Scheduling C%03d %s", i, command.type)
                rsp = self.schedule_command(generate_id(), command)
                if not rsp.result.success:
                    msg = f"tcode service schedule_command({command.type}) unsuccessful: {rsp.result.message} (see debug logs for stacktrace)"
                    if rsp.result.details is not None:
                        for line in rsp.result.details.get("traceback", "").split("\n"):
                            _logger.debug(line)
                    raise RuntimeError(msg)
        else:
            batch_size = 100

            for batch_index, command_batch in enumerate(batched(script.commands, batch_size)):
                commands_list = list(command_batch)
                scheduled_count = batch_index * batch_size + len(commands_list)
                _logger.info("Scheduled %d/%d commands", scheduled_count, total_commands)

                rsp_list = self.schedule_commands(
                    [(generate_id(), command) for command in commands_list]
                )
                for res in rsp_list:
                    if not res.result.success:
                        msg = (
                            "tcode service schedule_commands unsuccessful: "
                            f"{res.result.message} (see debug logs for stacktrace)"
                        )
                        if res.result.details is not None:
                            for line in res.result.details.get("traceback", "").split("\n"):
                                _logger.debug(line)
                        raise RuntimeError(msg)

        self.execute_run_loop()
