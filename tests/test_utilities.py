import unittest
from unittest.mock import patch
import tempfile
import pathlib

import tcode_api.api as tc
from tcode_api.utilities import (
    generate_tcode_script_from_protocol_designer,
    generate_new_tip_group_ids,
)


class TestGenerateTCodeScriptFromProtocolDesigner(unittest.TestCase):
    def test_generates_cli_options_then_tcode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            protocol = tmp_path / "protocol.tbw"
            protocol.write_text("{}", encoding="utf-8")
            pd_dir = tmp_path / "protocol-designer"
            pd_dir.mkdir(parents=True)

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
            # Ensure we did NOT default to protocol-designer's tracked template path.
            self.assertNotIn(str(pd_dir / "cli" / "cli-options.json"), first_cmd)

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

            cli_options_out = tmp_path / "existing-options.json"
            cli_options_out.write_text("{}", encoding="utf-8")

            with patch("tcode_api.utilities.subprocess.run", side_effect=fake_run) as run_mock:
                generate_tcode_script_from_protocol_designer(
                    protocol,
                    pd_dir,
                    tcode_out=tcode_out,
                    cli_options_out=cli_options_out,
                    create_cli_options=False,
                )

            self.assertEqual(len(run_mock.call_args_list), 1)


class TestGenerateNewTipGroupIds(unittest.TestCase):
    def test_rewrites_all_occurrences_consistently(self) -> None:
        script = tc.TCodeScript.new(name="test", description="")
        script.commands.append(
            tc.ADD_PIPETTE_TIP_GROUP(
                id="tipgroupA",
                descriptor=tc.PipetteTipGroupDescriptor(row_count=1, column_count=8),
            )
        )
        script.commands.append(tc.RETRIEVE_PIPETTE_TIP_GROUP(robot_id="robot1", id="tipgroupA"))
        script.commands.append(tc.RETRIEVE_PIPETTE_TIP_GROUP(robot_id="robot1", id="tipgroupA"))
        script.commands.append(
            tc.ADD_PIPETTE_TIP_GROUP(
                id="tipgroupB",
                descriptor=tc.PipetteTipGroupDescriptor(row_count=1, column_count=1),
            )
        )
        script.commands.append(tc.RETRIEVE_PIPETTE_TIP_GROUP(robot_id="robot1", id="tipgroupB"))

        with patch("tcode_api.utilities.generate_id", side_effect=["NEW_A", "NEW_B"]):
            rewritten = generate_new_tip_group_ids(script)

        # Original unchanged
        self.assertEqual(
            [
                getattr(c, "id", None)
                for c in script.commands
                if isinstance(c, (tc.ADD_PIPETTE_TIP_GROUP, tc.RETRIEVE_PIPETTE_TIP_GROUP))
            ],
            ["tipgroupA", "tipgroupA", "tipgroupA", "tipgroupB", "tipgroupB"],
        )

        ids = [
            c.id
            for c in rewritten.commands
            if isinstance(c, (tc.ADD_PIPETTE_TIP_GROUP, tc.RETRIEVE_PIPETTE_TIP_GROUP))
        ]
        self.assertEqual(ids, ["NEW_A", "NEW_A", "NEW_A", "NEW_B", "NEW_B"])
