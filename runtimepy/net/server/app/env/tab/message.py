"""
A module implementing a channel-environment tab message-handling interface.
"""

# built-in
import logging
from typing import Any

# internal
from runtimepy.channel import Channel
from runtimepy.net.server.app.env.tab.base import ChannelEnvironmentTabBase
from runtimepy.net.server.app.env.tab.logger import TabLogger, TabMessageSender
from runtimepy.net.stream.json.types import JsonMessage
from runtimepy.primitives import AnyPrimitive


class ChannelEnvironmentTabMessaging(ChannelEnvironmentTabBase):
    """A channel-environment tab interface."""

    shown: bool
    shown_ever: bool

    def init(self) -> None:
        """Initialize this instance."""

        super().init()
        self.shown = False
        self.shown_ever = False

        self.primitives: dict[str, AnyPrimitive] = {}
        self.callbacks: dict[str, int] = {}

    def _setup_callback(self, name: str, send: TabMessageSender) -> None:
        """Register a channel's value-change callback."""

        chan = self.command.env.field_or_channel(name)

        def callback(_, __) -> None:
            """Emit a change event to the stream."""

            # Render enumerations etc. here instead of trying to do it
            # in the UI.
            send({name: self.command.env.value(name)})

        if isinstance(chan, Channel):
            prim = chan.raw
            self.primitives[name] = prim
            self.callbacks[name] = prim.register_callback(callback)
        else:
            # Still need to handle bit-fields.
            self.command.logger.warning("%s", name)

    def handle_shown_state(
        self, shown: bool, outbox: JsonMessage, send: TabMessageSender
    ) -> None:
        """Handle 'shown' state changing."""

        self.shown = shown
        env = self.command.env

        if self.shown:
            # Send all values at once when switching tabs, but only the first
            # time.
            if not self.shown_ever:
                send(env.values())  # type: ignore
                self.shown_ever = True

            # Begin observing channel events for this environment.
            for name in env.names:
                self._setup_callback(name, send)
        else:
            # Remove callbacks for primitives.
            for name, val in self.callbacks.items():
                self.primitives[name].remove_callback(val)

        outbox["handle_shown_state"] = shown

    def handle_init(self, outbox: JsonMessage, send: TabMessageSender) -> None:
        """Handle tab initialization."""

        del outbox

        logger: logging.Logger = self.command.logger  # type: ignore

        # Add a log handler.
        logger.addHandler(TabLogger.create(send))

        logger.info("Tab initialized.")

    async def handle_message(
        self, data: dict[str, Any], send: TabMessageSender
    ) -> JsonMessage:
        """Handle a message from a tab."""

        kind: str = data["kind"]
        response: JsonMessage = {}

        # Respond to initialization.
        if kind == "init":
            self.handle_init(response, send)

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
                self.handle_shown_state(True, response, send)
            elif "hidden" in kind:
                self.handle_shown_state(False, response, send)

        # Log when messages aren't handled.
        else:
            self.command.logger.warning(
                "(%s) Message not handled: '%s'.", self.name, data
            )

        return response
