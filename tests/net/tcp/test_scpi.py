"""
Test the 'net.tcp.scpi' module.
"""

# built-in
import asyncio

# third-party
from pytest import mark

# module under test
from runtimepy.net.tcp import TcpConnection
from runtimepy.net.tcp.scpi import ScpiConnection


class MockScpiConnection(TcpConnection):
    """A sample connection class."""

    async def process_binary(self, data: bytes) -> bool:
        """Process a binary frame."""
        return await self.process_text(data.decode())

    async def process_text(self, data: str) -> bool:
        """Process a text frame."""

        for item in data.splitlines():
            match item:
                case "*IDN?":
                    self.send_text("Mock,Device,1.0")
                case _:
                    self.logger.error("Didn't handle message '%s'.", item)

        return True


@mark.asyncio
async def test_scpi_connection_basic():
    """Test basic interactions with a SCPI connection pair."""

    async with ScpiConnection.create_pair(peer=MockScpiConnection) as (
        server,
        client,
    ):
        event = asyncio.Event()

        # Start connection processing.
        processes = [
            asyncio.create_task(server.process(stop_sig=event)),
            asyncio.create_task(client.process(stop_sig=event)),
        ]

        # Initialize client.
        await client.initialized.wait()

        # We don't expect a response.
        await client.send_command("asdf", query=True, log=True, timeout=0.01)

        # End test.
        event.set()
        await asyncio.gather(*processes)
