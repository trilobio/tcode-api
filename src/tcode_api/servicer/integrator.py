"""
This file contains the base class for integrating TCode with external devices
"""

from pprint import pprint
from typing import Annotated

import fastapi
import uvicorn
from fastapi import BackgroundTasks, Body, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from tcode_api.servicer.client import TCodeServicerClient

TCODE_SERVER_DEFAULT_PORT = 8002

# This magic string is checked in tcode server to make sure
# everything is on the same version
MAGIC_STRING = "TCode integrator v1"


class WebHookBody(BaseModel):
    """The webhook request that is sent out with SEND_WEBHOOK

    :param timestamp: UNIX timestamp of the request in seconds
    :param fleet_name: Name of the fleet controller that triggered the request \
    :param destination_url: The destination URL of this request as specified in TCode. \
    This parameter can be useful if your integrator is behind a reverse-proxy or \
    is controlled by a third party.
    :param is_execution_paused: Whether the execution of the script is paused
    :param payload: The custom payload as specified. Max size 32KB.
    """

    timestamp: float
    fleet_name: str
    destination_url: str
    is_execution_paused: bool
    payload: str | None


class TCodeIntegratorBase:
    """
    The base class for TCodeIntegrator. Upon encountering SEND_WEBHOOK command,
    the control for TCode is transferred to subclass of this interface.
    """

    def __init__(self, tcode_server_host: str | None = None):
        """
        :param tcode_server_host: Optional. The tcode server hostname or IP address
         as a string without port or protocol (e.g. "production-fleet-06" or
         "192.168.8.3"). If not provided, the host will be inferred from incoming
         request. This inference should work if and only if the device running
         this integrator is connected to the same router as the fleet controller.
        """
        self.tcode_server_host = tcode_server_host
        # this will be set dynamically as requests come in
        self.incoming_request_host = None
        self.app = FastAPI()

        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            pprint(request)
            pprint(exc.errors())
            return fastapi.responses.JSONResponse(
                status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=fastapi.encoders.jsonable_encoder(exc.errors()),
            )

        @self.app.post("/")
        def _(
            args: Annotated[WebHookBody, Body()],
            request: Request,
            background_tasks: BackgroundTasks,
        ):

            if request.client is not None:
                self.incoming_request_host = request.client.host

            background_tasks.add_task(self.perform_action, args)

        @self.app.get("/")
        def _():
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
