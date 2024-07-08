"""
A module implementing an interface for classes with channel-command processors
that need to handle commands asynchronously.
"""

# built-in
from argparse import Namespace
import asyncio
from typing import Optional

# third-party
from vcorelib.logging import LoggerMixin

# internal
from runtimepy.channel.environment.command import FieldOrChannel
from runtimepy.channel.environment.command.parser import ChannelCommand
from runtimepy.channel.environment.command.processor import (
    ChannelCommandProcessor,
    CustomCommand,
)

ChannelCommandParams = tuple[Namespace, Optional[FieldOrChannel]]


class AsyncCommandProcessingMixin(LoggerMixin):
    """A class mixin for handling asynchronous commands."""

    command: ChannelCommandProcessor
    outgoing_commands: asyncio.Queue[ChannelCommandParams]

    def _setup_async_commands(self, *custom_commands: CustomCommand) -> None:
        """Setup asynchronous commands."""

        if not hasattr(self, "outgoing_commands"):
            self.outgoing_commands = asyncio.Queue()
            self.command.hooks.append(self._handle_command)

        self.command.register_custom_commands(*custom_commands)

    async def handle_command(
        self, args: Namespace, channel: Optional[FieldOrChannel]
    ) -> None:
        """Handle a command."""

    def _handle_command(
        self, args: Namespace, channel: Optional[FieldOrChannel]
    ) -> None:
        """Determine if a remote command should be queued up."""

        self.outgoing_commands.put_nowait((args, channel))

    async def process_command_queue(self) -> None:
        """Process any outgoing command requests."""

        while not self.outgoing_commands.empty():
            params = self.outgoing_commands.get_nowait()

            if params[0].command == ChannelCommand.CUSTOM:
                await self.command.handle_custom_command(*params)
            else:
                await self.handle_command(*params)

            self.outgoing_commands.task_done()
