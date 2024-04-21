"""
A module implementing a channel-environment tab message-handling interface.
"""

# built-in
import logging
from typing import Any, Callable, cast

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

        def callback(_, __) -> None:
            """Emit a change event to the stream."""

            # Render enumerations etc. here instead of trying to do it
            # in the UI.
            state.points[name].append(
                (
                    self.command.env.value(name),
                    cast(Channel[Any], chan).raw.last_updated_ns,
                )
            )

        assert isinstance(chan, Channel) or chan is not None
        prim = chan.raw
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

        if state.shown:
            # Send all values at once when switching tabs, but only the first
            # time.
            if not state.shown_ever:
                send(env.values())  # type: ignore
                state.shown_ever = True

            # Begin observing channel events for this environment.
            for name in env.names:
                self._setup_callback(name, state)
        else:
            # Remove callbacks for primitives.
            for name, val in state.callbacks.items():
                state.primitives[name].remove_callback(val)

        outbox["handle_shown_state"] = shown

    def handle_init(self, state: TabState) -> None:
        """Handle tab initialization."""

        # Initialize logging.
        if isinstance(self.command.logger, logging.Logger):
            state.add_logger(self.command.logger)

        self.command.logger.debug("Tab initialized.")

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

            cmd.logger.log(
                logging.INFO if result else logging.ERROR,
                "%s: %s",
                data["value"],
                result,
            )

        # Handle tab-event messages.
        elif kind.startswith("tab"):
            if "shown" in kind:
                self.handle_shown_state(True, response, send, state)
            elif "hidden" in kind:
                self.handle_shown_state(False, response, send, state)

        # Log when messages aren't handled.
        else:
            self.command.logger.warning(
                "(%s) Message not handled: '%s'.", self.name, data
            )

        return response
