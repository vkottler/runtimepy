"""
A module implementing a simple WebSocket server for the package.
"""

# internal
from runtimepy.net.arbiter.tcp.json import WebsocketJsonMessageConnection
from runtimepy.net.server.app.env.tab import ChannelEnvironmentTab
from runtimepy.net.server.app.env.tab.logger import TabMessageSender
from runtimepy.net.server.struct import UiState
from runtimepy.net.stream.json.types import JsonMessage
from runtimepy.net.websocket import WebsocketConnection


class RuntimepyWebsocketConnection(WebsocketJsonMessageConnection):
    """A class implementing a package-specific WebSocket connection."""

    send_interfaces: dict[str, TabMessageSender]
    ui_time: float

    def tab_sender(self, name: str) -> TabMessageSender:
        """Get a tab message-sending interface."""

        if name not in self.send_interfaces:

            def sender(data: JsonMessage) -> None:
                """Tab-message sending interface."""
                self.send_json({"ui": {name: data}})

            self.send_interfaces[name] = sender

        return self.send_interfaces[name]

    def _poll_ui_state(self, ui: UiState, time: float) -> None:
        """Update UI-specific state."""

        # Update time.
        ui.env["time"] = time

        # Update connection metrics.
        ui.json_metrics.update(self.metrics)

    def _register_handlers(self) -> None:
        """Register connection-specific command handlers."""

        super()._register_handlers()
        self.send_interfaces = {}
        self.ui_time = 0.0

        async def ui_handler(outbox: JsonMessage, inbox: JsonMessage) -> None:
            """A simple loopback handler."""

            # Handle frame messages.
            if "time" in inbox:
                ui_time = inbox["time"]

                # Poll UI state.
                ui = UiState.singleton()
                if ui and ui.env.finalized:
                    self._poll_ui_state(ui, ui_time)

                # Allows tabs to respond on a per-frame basis.
                for name, tab in ChannelEnvironmentTab.all_tabs.items():
                    result = tab.handle_frame(ui_time)
                    if result:
                        outbox[name] = result

            # Handle messages from tabs.
            elif "name" in inbox and "event" in inbox:
                name = inbox["name"]
                try_tab = ChannelEnvironmentTab.all_tabs.get(name)
                if try_tab is not None:
                    response = await try_tab.handle_message(
                        inbox["event"], self.tab_sender(name)
                    )
                    if response:
                        outbox[name] = response

        self.basic_handler("ui", ui_handler)


class RuntimepyDataWebsocketConnection(WebsocketConnection):
    """A class implementing a WebSocket connection for streaming raw data."""
