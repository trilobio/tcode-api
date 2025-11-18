"""Jog Control interface and multiple interface implementations."""

from tcode_api.servicer import TCodeServicerClient


class JogControlInterface:
    """Interface for jogging implementations."""

    def __init__(self, client: TCodeServicerClient) -> None:
        self.client = client

    def start(self) -> None:
        """Start the jogging interface."""
        self.client.set_run_state(True)
