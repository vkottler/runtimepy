"""
A module implementing a channel-environment tab message-handling interface.
"""

# built-in
import logging
from typing import Any

# internal
from runtimepy.net.server.app.env.tab.base import ChannelEnvironmentTabBase
from runtimepy.net.server.app.env.tab.logger import TabLogger, TabMessageSender
from runtimepy.net.stream.json.types import JsonMessage


class ChannelEnvironmentTabMessaging(ChannelEnvironmentTabBase):
    """A channel-environment tab interface."""

    shown: bool

    def init(self) -> None:
        """Initialize this instance."""

        super().init()
        self.shown = False

    def handle_shown_state(self, shown: bool, outbox: JsonMessage) -> None:
        """Handle 'shown' state changing."""

        self.shown = shown

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
                self.handle_shown_state(True, response)
            elif "hidden" in kind:
                self.handle_shown_state(False, response)

        # Log when messages aren't handled.
        else:
            self.command.logger.warning("Message not handled: '%s'.", data)

        return response
