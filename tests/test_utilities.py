import unittest
from unittest.mock import patch
import tempfile
import pathlib

import tcode_api.api as tc
from tcode_api.utilities import (
    generate_tcode_script_from_protocol_designer,
    load_labware,
    remove_add_create_labware_commands,
)


class TestRemoveAddCreateLabwareCommands(unittest.TestCase):
    def test_removes_add_and_create_labware_only(self) -> None:
        script = tc.TCodeScript.new(name="test", description="")
        script.commands.append(tc.ADD_LABWARE(id="plate1", descriptor=tc.WellPlateDescriptor()))
        script.commands.append(tc.COMMENT(text="keep me"))

        labware_description = load_labware("checkit_50ul")
        script.commands.append(
            tc.CREATE_LABWARE(
                robot_id="robot1",
                description=labware_description,
                holder=tc.LabwareHolderName(robot_id="robot1", name="1"),
            )
        )

        filtered = remove_add_create_labware_commands(script)

        # Original is unchanged by default
        self.assertEqual(len(script.commands), 3)
        # Filtered has only the non-labware commands
        self.assertEqual(len(filtered.commands), 1)
        self.assertIsInstance(filtered.commands[0], tc.COMMENT)

    def test_inplace(self) -> None:
        script = tc.TCodeScript.new(name="test", description="")
        script.commands.append(tc.ADD_LABWARE(id="trash", descriptor=tc.TrashDescriptor()))
        script.commands.append(tc.COMMENT(text="keep"))

        same = remove_add_create_labware_commands(script, inplace=True)
        self.assertIs(same, script)
        self.assertEqual(len(script.commands), 1)
        self.assertIsInstance(script.commands[0], tc.COMMENT)


class TestGenerateTCodeScriptFromProtocolDesigner(unittest.TestCase):
    def test_generates_cli_options_then_tcode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            protocol = tmp_path / "protocol.tbw"
            protocol.write_text("{}", encoding="utf-8")
            pd_dir = tmp_path / "protocol-designer"
            pd_dir.mkdir(parents=True)

            cli_options_out = pathlib.Path("/tmp/cli-options.json")
            tcode_out = tmp_path / "out.tc"
            expected = tc.TCodeScript.new(name="x", description="")

            def fake_run(cmd, cwd=None, check=None):
                # When generate-tcode runs, write the output file the wrapper will parse.
                if isinstance(cmd, list) and "cli/generate-tcode.ts" in cmd:
                    tcode_out.write_text(expected.model_dump_json(), encoding="utf-8")
                return None

            with patch("tcode_api.utilities.subprocess.run", side_effect=fake_run) as run_mock:
                script = generate_tcode_script_from_protocol_designer(
                    protocol,
                    pd_dir,
                    tcode_out=tcode_out,
                    cli_options_out=cli_options_out,
                    create_cli_options=True,
                    set_overrides=["useMC8P300=false"],
                    symbol_overrides=["numSteps=5"],
                    pnpm="pnpm",
                )

            self.assertIsInstance(script, tc.TCodeScript)
            self.assertEqual(len(run_mock.call_args_list), 2)
            first_cmd = run_mock.call_args_list[0].args[0]
            second_cmd = run_mock.call_args_list[1].args[0]
            self.assertIn("cli/create-cli-options.ts", first_cmd)
            self.assertIn("--set", first_cmd)
            self.assertIn("useMC8P300=false", first_cmd)
            self.assertIn("--symbol", first_cmd)
            self.assertIn("numSteps=5", first_cmd)
            self.assertIn("cli/generate-tcode.ts", second_cmd)

    def test_skips_cli_options_step(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            protocol = tmp_path / "protocol.tbw"
            protocol.write_text("{}", encoding="utf-8")
            pd_dir = tmp_path / "protocol-designer"
            pd_dir.mkdir(parents=True)
            tcode_out = tmp_path / "out.tc"
            expected = tc.TCodeScript.new(name="x", description="")

            def fake_run(cmd, cwd=None, check=None):
                if isinstance(cmd, list) and "cli/generate-tcode.ts" in cmd:
                    tcode_out.write_text(expected.model_dump_json(), encoding="utf-8")
                return None

            with patch("tcode_api.utilities.subprocess.run", side_effect=fake_run) as run_mock:
                generate_tcode_script_from_protocol_designer(
                    protocol,
                    pd_dir,
                    tcode_out=tcode_out,
                    create_cli_options=False,
                )

            self.assertEqual(len(run_mock.call_args_list), 1)
