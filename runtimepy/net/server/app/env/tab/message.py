"""
A module implementing a channel-environment tab message-handling interface.
"""

# built-in
import logging
from typing import Any, Callable

# internal
from runtimepy.channel import Channel
from runtimepy.message import JsonMessage
from runtimepy.net.server.app.env.tab.base import ChannelEnvironmentTabBase
from runtimepy.net.server.websocket.state import TabState

TabMessageSender = Callable[[JsonMessage], None]


class ChannelEnvironmentTabMessaging(ChannelEnvironmentTabBase):
    """A channel-environment tab interface."""

    def _setup_callback(self, name: str, state: TabState) -> None:
        """Register a channel's value-change callback."""

        chan = self.command.env.field_or_channel(name)
        assert isinstance(chan, Channel) or chan is not None
        prim = chan.raw

        def callback(_, __) -> None:
            """Emit a change event to the stream."""

            # Render enumerations etc. here instead of trying to do it
            # in the UI.
            state.points[name].append(
                (self.command.env.value(name), prim.last_updated_ns)
            )

        state.primitives[name] = prim
        state.callbacks[name] = prim.register_callback(callback)

    def handle_shown_state(
        self,
        shown: bool,
        outbox: JsonMessage,
        send: TabMessageSender,
        state: TabState,
    ) -> None:
        """Handle 'shown' state changing."""

        state.shown = shown
        env = self.command.env

        # Always sample current values.
        latest = env.values()

        if state.shown:
            # Send missing or changed values.
            if latest != state.latest_ui_values:
                to_send = {}
                for key, value in latest.items():
                    if (
                        key not in state.latest_ui_values
                        or state.latest_ui_values[key] != value
                    ):
                        to_send[key] = value

                send(to_send)  # type: ignore

            # Begin observing channel events for this environment.
            for name in env.names:
                self._setup_callback(name, state)
        else:
            # Remove callbacks for primitives.
            for name, val in state.callbacks.items():
                state.primitives[name].remove_callback(val)

        # Save current UI state.
        state.latest_ui_values.update(latest)

        outbox["handle_shown_state"] = shown

    def handle_init(self, state: TabState) -> None:
        """Handle tab initialization."""

        # Initialize logging.
        if isinstance(self.logger, logging.Logger):
            state.add_logger(self.logger)

        self.logger.debug("Tab initialized.")

    async def handle_message(
        self, data: dict[str, Any], send: TabMessageSender, state: TabState
    ) -> JsonMessage:
        """Handle a message from a tab."""

        kind: str = data["kind"]
        response: JsonMessage = {}

        # Respond to initialization.
        if kind == "init":
            self.handle_init(state)

        # Handle command-line commands.
        elif kind == "command":
            cmd = self.command
            result = cmd.command(data["value"])

            # Limit log spam.
            self.governed_log(
                self.log_limiter,
                "%s: %s",
                data["value"],
                result,
                level=logging.INFO if result else logging.ERROR,
            )

        # Handle tab-event messages.
        elif kind.startswith("tab"):
            if "shown" in kind:
                self.handle_shown_state(True, response, send, state)
            elif "hidden" in kind:
                self.handle_shown_state(False, response, send, state)

        # Log when messages aren't handled.
        else:
            self.governed_log(
                self.log_limiter,
                "(%s) Message not handled: '%s'.",
                self.name,
                data,
                level=logging.WARNING,
            )

        return response
