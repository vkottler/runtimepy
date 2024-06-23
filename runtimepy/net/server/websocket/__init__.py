"""
A module implementing a simple WebSocket server for the package.
"""

# built-in
from collections import defaultdict
from typing import Optional

# third-party
from vcorelib.math import RateLimiter, metrics_time_ns, to_nanos

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

    poll_governor: RateLimiter
    poll_connection_metrics: bool

    _ui: Optional[UiState]

    def tab_sender(self, name: str) -> TabMessageSender:
        """Get a tab message-sending interface."""

        if name not in self.send_interfaces:

            def sender(data: JsonMessage) -> None:
                """Tab-message sending interface."""
                self.send_json({"ui": {name: data}})

            self.send_interfaces[name] = sender

        return self.send_interfaces[name]

    def _get_ui(self) -> Optional[UiState]:
        """Obtain a reference to a possible user interface struct."""

        if self._ui is None:
            ui = UiState.singleton()

            if ui is not None and ui.env.finalized:

                def check_metrics_poll(_: int, curr: int) -> None:
                    """
                    Register change handler on 'num_connections' primitive.
                    """

                    self.poll_connection_metrics = (
                        self.poll_connection_metrics or curr == 1
                    )

                chan, _ = ui.env["num_connections"]
                chan.raw.register_callback(check_metrics_poll)  # type: ignore

                # Add to num_connections.
                ui.env.add_int("num_connections", 1)
                self._ui = ui

        return self._ui

    def _poll_ui_state(self, ui: UiState, time: float) -> None:
        """Update UI-specific state."""

        # Only one connection needs to perform this task.
        if self.poll_connection_metrics and self.poll_governor():
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

            # Handle frame messages.
            if "time" in inbox:
                # Poll UI state.
                ui = self._get_ui()
                if ui:
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

        # Limit UI metrics update rate to 250 Hz.
        self.poll_governor = RateLimiter(
            to_nanos(1.0 / 250.0), source=metrics_time_ns
        )

        self.poll_connection_metrics = False
        self._ui = None

    async def async_init(self) -> bool:
        """A runtime initialization routine (executes during 'process')."""

        result = await super().async_init()

        self._get_ui()

        return result

    def disable_extra(self) -> None:
        """Additional tasks to perform when disabling."""

        # Disable loggers when the connection closes.
        for state in self.tabs.values():
            state.clear_loggers()

        # Subtract from num_connections.
        ui = self._get_ui()
        if ui:
            self.poll_connection_metrics = False
            ui.env.add_int("num_connections", -1)


class RuntimepyDataWebsocketConnection(WebsocketConnection):
    """A class implementing a WebSocket connection for streaming raw data."""
