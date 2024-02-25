"""
A module implementing an interface for classes with channel-command processors
that need to handle commands asynchronously.
"""

# built-in
from abc import ABC, abstractmethod
from argparse import Namespace
import asyncio
from typing import Optional

# third-party
from vcorelib.logging import LoggerMixin

# internal
from runtimepy.channel.environment.command import FieldOrChannel
from runtimepy.channel.environment.command.processor import (
    ChannelCommandProcessor,
)

ChannelCommandParams = tuple[Namespace, Optional[FieldOrChannel]]


class AsyncCommandProcessingMixin(LoggerMixin, ABC):
    """A class mixin for handling asynchronous commands."""

    command: ChannelCommandProcessor
    outgoing_commands: asyncio.Queue[ChannelCommandParams]

    def _setup_async_commands(self) -> None:
        """Setup asynchronous commands."""

        if not hasattr(self, "outgoing_commands"):
            self.outgoing_commands = asyncio.Queue()
            self.command.hooks.append(self._handle_command)

    @abstractmethod
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
            await self.handle_command(*self.outgoing_commands.get_nowait())
            self.outgoing_commands.task_done()
