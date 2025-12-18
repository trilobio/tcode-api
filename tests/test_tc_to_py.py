import pathlib
import unittest
import tempfile
from tcode_api import tc_to_py
import tcode_api.api as tc

class TestTcToPyMethod(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir_path = pathlib.Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_hardcoded_script(self) -> None:
        """Test that tests/data/example_script.tc converted to python and then run returns an identical .tc script."""
        tc_file_path = pathlib.Path(__file__).parent / "data" / "example_script.tc"
        output_tc_file_path = self.temp_dir_path / "output_example_script.tc"
        self.assertFalse(output_tc_file_path.exists())

        with tc_file_path.open('r') as f:
            original_tc_content = f.read()
            f.seek(0)
            script = tc.TCodeScript.read(f)

        # Invocation under test
        python_script = tc_to_py(script, output_tc_file_path)

        try:
            exec(python_script)
        except Exception as e:
            print("-" * 100)
            print("| Error executing generated Python script:")
            lines = python_script.split('\n')
            for i, line in enumerate(lines, start=1):
                print(f"| {i:4}: {line}")
            print("-" * 100)
            raise e

        self.assertTrue(output_tc_file_path.exists())

        with open(output_tc_file_path, 'r') as output_tc_file:
            output_tc_content = output_tc_file.read()

        # Assert that the contents are identical
        breakpoint()
        self.assertEqual(original_tc_content, output_tc_content)
