"""
A module implementing a simple WebSocket server for the package.
"""

# internal
from runtimepy.net.arbiter.tcp.json import WebsocketJsonMessageConnection


class RuntimepyWebsocketConnection(WebsocketJsonMessageConnection):
    """A class implementing a package-specific WebSocket connection."""

    def _register_handlers(self) -> None:
        """Register connection-specific command handlers."""

        super()._register_handlers()
        print("TODO")
