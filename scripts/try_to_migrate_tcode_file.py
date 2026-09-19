import sys
import json

from tcode_api.api import TCodeScript, Metadata
from tcode_api.api.compat import load_api_object

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        j = json.load(f)

    api_version = j["metadata"]["tcode_api_version"]
    commands = []
    for c in j["commands"]:
        commands.append(load_api_object(c, api_version=api_version))
    script = TCodeScript(metadata=Metadata(**j["metadata"]), commands=commands)
    breakpoint()
