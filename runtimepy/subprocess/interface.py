"""
A module implementing a runtimepy peer interface.
"""

# built-in
import sys

# third-party
from vcorelib.logging import LoggerMixin

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.channel.environment.command.processor import (
    ChannelCommandProcessor,
)
from runtimepy.message import MessageProcessor
from runtimepy.net.stream.json.interface import JsonMessageInterface


class RuntimepyPeerInterface(JsonMessageInterface, LoggerMixin):
    """A class implementing an interface for messaging peer subprocesses."""

    def __init__(self, env: ChannelEnvironment, **kwargs) -> None:
        """Initialize this instance."""

        LoggerMixin.__init__(self)
        self.processor = MessageProcessor()
        self.command = ChannelCommandProcessor(env, self.logger, **kwargs)

        JsonMessageInterface.__init__(self)

    def handle_stderr(self, data: bytes) -> None:
        """Forward stderr."""
        print(data.decode(), file=sys.stderr)

    async def handle_stdout(self, data: bytes) -> None:
        """Handle messages from stdout."""

        for msg in self.processor.messages(data):
            await self.process_json(msg)
