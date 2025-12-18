"""Tooling for reformatting TCodeSripts in various representations."""

import copy
import pathlib
import re

import black

import tcode_api.api as tc


def tc_to_py(script: tc.TCodeScript, filepath: pathlib.Path | None = None) -> str:
    """Generate a Python script that, when executed, produced the given TCodeScript.

    :param script: The TCodeScript  object to convert.
    :param filepath: If given, script will end by writing itself to this filepath. The written file
        will be identical to the file that would be written by calling script.write().

    :return: A string containing the Python script.
    """
    raw_python_lines = [
        f'"""Auto-generated Python script to reproduce "{script.metadata.name}"',
        "",
        f"   description: {script.metadata.description or 'No description provided.'}",
        f"   tcode-api version: {script.metadata.tcode_api_version}",
        # Skipping timestamp representation, cause it makes char-for-char comparison of scripts in
        # the unittesting of this method more difficult.
        # f"   timestamp: {script.metadata.timestamp}",
        '"""',
        "",
        "from tcode_api import api as tc",
        "",
        # the 'tc.' prefix will be added later to TCodeScript
        f"script = TCodeScript.new(name='{script.metadata.name}', description={script.metadata.description})",
        "",
    ]

    # Convert the TCodeScript commands
    for command in script.commands:
        raw_python_lines.append(f"script.commands.append({repr(command)})")

    if filepath is not None:
        tc_filepath = filepath.with_suffix(".tc")
        raw_python_lines.append("")
        raw_python_lines.append(f"with open(r'{str(tc_filepath)}', 'w') as f:")
        raw_python_lines.append("    script.write(f)")

    raw_python_script = "\n".join(raw_python_lines)

    # Remove all `type=...` kwarg specifications from the generated code
    raw_python_script = re.sub(r"type=[^,\)]+, ", "", raw_python_script)

    # Fix references for all objects in the tcode_api.api module
    object_names = copy.deepcopy(tc.__all__)
    # object_names.remove("TCodeScript")  # handled separately
    object_names.sort(key=len, reverse=True)
    raw_python_script = re.sub(r"\b(" + "|".join(object_names) + r")\b", r"tc.\1", raw_python_script)

    # Replace longer names first to avoid partial, otherwise you get incorrect replacements.
    # Example:
    #    'PipetteDescriptor' comes before 'SingleChannelPipetteDescriptor' in tc.__all__, which
    #    causes stuff like 'SingleChanneltc.PipetteDescriptor'

    # for object_name in object_names:
    #     if object_name in ["TCodeScript"]:
    #         continue
    #     raw_python_script = raw_python_script.replace(object_name, f"tc.{object_name}")

    formatted_python_script = black.format_str(raw_python_script, mode=black.Mode())
    return formatted_python_script
