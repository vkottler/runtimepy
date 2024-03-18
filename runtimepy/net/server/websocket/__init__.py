"""
A module implementing a simple WebSocket server for the package.
"""

# internal
from runtimepy.net.arbiter.tcp.json import WebsocketJsonMessageConnection
from runtimepy.net.stream.json.types import JsonMessage
from runtimepy.net.websocket import WebsocketConnection


class RuntimepyWebsocketConnection(WebsocketJsonMessageConnection):
    """A class implementing a package-specific WebSocket connection."""

    def _register_handlers(self) -> None:
        """Register connection-specific command handlers."""

        super()._register_handlers()

        async def ui_handler(outbox: JsonMessage, inbox: JsonMessage) -> None:
            """A simple loopback handler."""

            self.logger.info("Got UI message: %s.", inbox)

            # Connect tabs to tab messaging somehow.
            outbox[inbox["name"]] = {"GOOD_SHIT": "BUD"}

        self.basic_handler("ui", ui_handler)


class RuntimepyDataWebsocketConnection(WebsocketConnection):
    """A class implementing a WebSocket connection for streaming raw data."""
