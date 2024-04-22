"""
A module implementing a JSON message connection interface.
"""

# built-in
from argparse import Namespace
from json import JSONDecodeError, loads
from typing import Optional

# internal
from runtimepy.channel.environment.command import FieldOrChannel
from runtimepy.message.interface import JsonMessageInterface
from runtimepy.mixins.async_command import AsyncCommandProcessingMixin
from runtimepy.net.stream.string import StringMessageConnection


class JsonMessageConnection(
    StringMessageConnection, AsyncCommandProcessingMixin, JsonMessageInterface
):
    """A connection interface for JSON messaging."""

    def init(self) -> None:
        """Initialize this instance."""

        super().init()
        self._setup_async_commands()
        JsonMessageInterface.__init__(self)

    def write(self, data: bytes, addr: tuple[str, int] = None) -> None:
        """Write data."""
        self._send_message(data, addr=addr)

    async def handle_command(
        self, args: Namespace, channel: Optional[FieldOrChannel]
    ) -> None:
        """Handle a remote command asynchronously."""

        if args.remote and self.connected:
            cli_args = [args.command]
            if args.force:
                cli_args.append("-f")
            cli_args.append(args.channel)

            self.logger.info(
                "Remote command: %s",
                await self.channel_command(
                    " ".join(cli_args + args.extra), environment=args.env
                ),
            )

    async def async_init(self) -> bool:
        """A runtime initialization routine (executes during 'process')."""

        # Check loopback if it makes sense to.
        result = await super().async_init()

        # Only not-connected UDP connections can't do this.
        if self.connected:
            result = await self.loopback()

            if result:
                await self.wait_json({"meta": self.meta})

        return result

    async def process_message(
        self, data: str, addr: tuple[str, int] = None
    ) -> bool:
        """Process a string message."""

        result = True

        try:
            decoded = loads(data)

            if decoded and isinstance(decoded, dict):
                result = await self.process_json(decoded, addr=addr)
            else:
                self.logger.error("Ignoring message '%s'.", data)
        except JSONDecodeError as exc:
            self.logger.exception("Couldn't decode '%s': %s", data, exc)

        return result
