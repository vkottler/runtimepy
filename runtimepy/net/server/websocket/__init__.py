"""
A module implementing a simple WebSocket server for the package.
"""

# internal
from runtimepy.net.arbiter.tcp.json import WebsocketJsonMessageConnection
from runtimepy.net.server.app.env.tab import ChannelEnvironmentTab
from runtimepy.net.server.app.env.tab.logger import TabMessageSender
from runtimepy.net.stream.json.types import JsonMessage
from runtimepy.net.websocket import WebsocketConnection


class RuntimepyWebsocketConnection(WebsocketJsonMessageConnection):
    """A class implementing a package-specific WebSocket connection."""

    send_interfaces: dict[str, TabMessageSender]

    def tab_sender(self, name: str) -> TabMessageSender:
        """Get a tab message-sending interface."""

        if name not in self.send_interfaces:

            def sender(data: JsonMessage) -> None:
                """Tab-message sending interface."""
                self.send_json({"ui": {name: data}})

            self.send_interfaces[name] = sender

        return self.send_interfaces[name]

    def _register_handlers(self) -> None:
        """Register connection-specific command handlers."""

        super()._register_handlers()
        self.send_interfaces = {}

        async def ui_handler(outbox: JsonMessage, inbox: JsonMessage) -> None:
            """A simple loopback handler."""

            # Handle messages from tabs.
            if "name" in inbox and "event" in inbox:
                name = inbox["name"]
                tab = ChannelEnvironmentTab.all_tabs.get(name)
                if tab is not None:
                    response = await tab.handle_message(
                        inbox["event"], self.tab_sender(name)
                    )
                    if response:
                        outbox[name] = response

        self.basic_handler("ui", ui_handler)


class RuntimepyDataWebsocketConnection(WebsocketConnection):
    """A class implementing a WebSocket connection for streaming raw data."""
