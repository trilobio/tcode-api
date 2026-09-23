import json
import sys
from typing import cast

from tcode_api.api import Metadata, TCode, TCodeScript
from tcode_api.api.compat import load_api_object

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        j = json.load(f)

    api_version = j["metadata"]["tcode_api_version"]
    commands: list[TCode] = []
    for c in j["commands"]:
        commands.append(cast(TCode, load_api_object(c, api_version=api_version)))
    script = TCodeScript(metadata=Metadata(**j["metadata"]), commands=commands)
    breakpoint()
