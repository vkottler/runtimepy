"""
A module implementing a simple WebSocket server for the package.
"""

# built-in
from collections import defaultdict

# internal
from runtimepy.message import JsonMessage
from runtimepy.net.arbiter.tcp.json import WebsocketJsonMessageConnection
from runtimepy.net.server.app.env.tab import ChannelEnvironmentTab
from runtimepy.net.server.app.env.tab.message import TabMessageSender
from runtimepy.net.server.struct import UiState
from runtimepy.net.server.websocket.state import TabState
from runtimepy.net.websocket import WebsocketConnection


class RuntimepyWebsocketConnection(WebsocketJsonMessageConnection):
    """A class implementing a package-specific WebSocket connection."""

    send_interfaces: dict[str, TabMessageSender]
    ui_time: float
    tabs: dict[str, TabState]

    # The first UI client has exclusive access to some functions, like
    # polling metrics.
    first_client: bool
    first_message: bool

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

        # Only one connection needs to perform this task.
        if self.first_client or ui.env.value("num_connections") == 1:
            # Update time.
            ui.env["time_ms"] = time
            ui.env["frame_period_ms"] = time - self.ui_time

            # Update connection metrics.
            ui.json_metrics.update(self.metrics)

            # Update other metrics.
            ui.poll()

    def _register_handlers(self) -> None:
        """Register connection-specific command handlers."""

        super()._register_handlers()

        async def ui_handler(outbox: JsonMessage, inbox: JsonMessage) -> None:
            """A simple loopback handler."""

            # Add to num_connections.
            if self.first_message:
                ui = UiState.singleton()
                if ui and ui.env.finalized:
                    self.first_client = (
                        ui.env.add_int("num_connections", 1) == 1
                    )
                self.first_message = False

            # Handle frame messages.
            if "time" in inbox:
                # Poll UI state.
                ui = UiState.singleton()
                if ui and ui.env.finalized:
                    self._poll_ui_state(ui, inbox["time"])

                # Allows tabs to respond on a per-frame basis.
                for name in ChannelEnvironmentTab.all_tabs:
                    result = self.tabs[name].frame(inbox["time"])
                    if result:
                        outbox[name] = result

                self.ui_time = inbox["time"]

            # Handle messages from tabs.
            elif "name" in inbox and "event" in inbox:
                name = inbox["name"]

                try_tab = ChannelEnvironmentTab.all_tabs.get(name)
                if try_tab is not None:
                    response = await try_tab.handle_message(
                        inbox["event"], self.tab_sender(name), self.tabs[name]
                    )
                    if response:
                        outbox[name] = response

        self.basic_handler("ui", ui_handler)

    def init(self) -> None:
        """Initialize this instance."""

        super().init()

        self.send_interfaces = {}
        self.ui_time = 0.0
        self.tabs = defaultdict(TabState.create)
        self.first_client = False
        self.first_message = True

    def disable_extra(self) -> None:
        """Additional tasks to perform when disabling."""

        # Disable loggers when the connection closes.
        for state in self.tabs.values():
            state.clear_loggers()

        # Subtract from num_connections.
        ui = UiState.singleton()
        if ui and ui.env.finalized:
            ui.env.add_int("num_connections", -1)


class RuntimepyDataWebsocketConnection(WebsocketConnection):
    """A class implementing a WebSocket connection for streaming raw data."""
