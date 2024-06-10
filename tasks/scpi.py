"""
A module implementing an SCPI interface.
"""

# built-in
import asyncio

# internal
from runtimepy.net.arbiter.tcp import TcpConnectionFactory
from runtimepy.net.tcp import TcpConnection


class ScpiConnection(TcpConnection):
    """A simple SCPI connection class."""

    def init(self) -> None:
        """Initialize this instance."""

        self.command_lock = asyncio.Lock()
        self.message_queue: asyncio.Queue[str] = asyncio.Queue(maxsize=1)

    async def async_init(self) -> bool:
        """Initialize this instance."""

        self.logger.info(await self.send_command("*IDN?"))

        return True

    async def process_text(self, data: str) -> bool:
        """Process a text frame."""

        for item in data.split("\r\n"):
            if item:
                await self.message_queue.put(item)

        return True

    async def process_binary(self, data: bytes) -> bool:
        """Process a binary frame."""
        return await self.process_text(data.decode())

    async def send_command(self, command: str, response: bool = True) -> str:
        """Send a command."""

        async with self.command_lock:
            self.send_text(command + "\n")

            result = ""
            if response:
                result = await self.message_queue.get()

        return result


class ScpiConn(TcpConnectionFactory[ScpiConnection]):
    """A connection factory for SCPI devices."""

    kind = ScpiConnection
