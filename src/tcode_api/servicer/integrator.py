from typing import Annotated

import uvicorn
from fastapi import Body, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from tcode_api.api.commands import WebHookBody
from tcode_api.servicer.client import TCodeServicerClient

TCODE_SERVER_DEFAULT_PORT = 8002

# This magic string is checked in tcode server to make sure
# everything is on the same version
MAGIC_STRING = f"TCode integrator v1"


class TCodeIntegratorBase:
    def __init__(self, tcode_server_host: str | None = None):
        self.tcode_server_host = tcode_server_host
        # this will be set dynamically as requests come in
        self.incoming_request_host = None
        self.app = FastAPI()

        @self.app.post("/")
        def handler(args: Annotated[WebHookBody, Body()], request: Request):
            if request.client is not None:
                self.incoming_request_host = request.client.host
            self.perform_action(args)

        @self.app.get("/")
        def handler():
            return f"{MAGIC_STRING} {self.__class__.__name__}"

    def resume_tcode(self):
        server_host = self.tcode_server_host or self.incoming_request_host
        server_url = None
        if server_host is not None:
            server_url = f"http://{server_host}:{TCODE_SERVER_DEFAULT_PORT}"
        client = TCodeServicerClient(server_url)
        client.set_run_state(True)

    def serve(self, host: str = "0.0.0.0", port: int = 8092):
        uvicorn.run(self.app, host=host, port=port)

    def perform_action(self, data: WebHookBody):
        raise NotImplementedError
