"""Generate a python script from a .tc file."""

import pathlib

import plac  # type: ignore [import-untyped]

import tcode_api.api as tc
from tcode_api import tc_to_py


@plac.annotations(
    tc_file=plac.Annotation("Filepath for input .tc file", type=pathlib.Path),
    py_file=plac.Annotation(
        "Filepath for output .py file", kind="option", abbrev="o", type=pathlib.Path
    ),
)
def main(tc_file: pathlib.Path, py_file: pathlib.Path | None = None) -> None:
    """Generate a python script from a .tc file.

    :param tc_file: Filepath for input .tc file
    :param py_file: Filepath for output .py file. If None, defaults to the same name as tc_file
        with .py extension.
    """
    if py_file is None:
        py_file = tc_file.with_suffix(".py")

    script: tc.TCodeScript
    with tc_file.open("r") as f:
        script = tc.TCodeScript.read(f)

    py_code = tc_to_py(script, filepath=py_file)

    with py_file.open("w") as f:
        f.write(py_code)
        print(f"Wrote python script to {py_file}")


if __name__ == "__main__":
    plac.call(main)
