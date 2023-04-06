"""
Test the 'net.tcp.telnet' module.
"""

# built-in
import asyncio
from typing import BinaryIO

# third-party
from pytest import mark

# module under test
from runtimepy.net.tcp.telnet import NEWLINE, Telnet, TelnetCode, TelnetNvt


class SimpleTelnet(Telnet):
    """A simple telnet implementation."""

    async def process_text(self, data: str) -> bool:
        """Process a text frame."""

        self.logger.info("Text: '%s'.", data)
        return True

    async def process_command(self, code: TelnetCode) -> None:
        """Process a telnet command."""
        self.logger.info("Command: %s (%d).", code, code)

        if code is TelnetCode.IP:
            self.disable("Interrupt Process")

    async def handle_nvt(self, action: TelnetNvt) -> None:
        """Handle a signal for the network virtual-terminal."""
        self.logger.info("NVT signal: %s (%d).", action, action)

    async def process_option(
        self, code: TelnetCode, option: int, _: BinaryIO
    ) -> None:
        """Process a telnet option."""
        self.logger.info("Option: %s (%d), %d", code, code, option)


@mark.asyncio
async def test_telnet_connection_basic():
    """Test basic interactions with a telnet connection pair."""

    conn1, conn2 = await SimpleTelnet.create_pair()

    async def run_test() -> None:
        """
        Ensure each side of the connection is being processed to give a chance
        for messages to be processed.
        """

        conn1.send_text("Hello, world!")
        conn1.send_binary(NEWLINE)
        conn2.send_text("Hello, world!")
        conn2.send_binary(NEWLINE)

        conn1.send_option(TelnetCode.DO, 100)
        conn2.send_option(TelnetCode.WILL, 100)

        # Ensure these messages get sent.
        await asyncio.sleep(0.1)

        conn1.send_binary(bytes([TelnetCode.IAC, TelnetCode.IAC]))
        conn2.send_binary(bytes([TelnetCode.IAC, TelnetCode.IAC]))

        conn1.send_command(TelnetCode.IP)
        conn2.send_command(TelnetCode.IP)

    async def conn_disabler(timeout: float, poll_period: float = 0.05) -> None:
        """Disable the connections after some timeout."""

        total_time = 0.0
        while not conn1.disabled or not conn2.disabled:
            await asyncio.sleep(poll_period)
            total_time += poll_period

            if total_time >= timeout:
                conn1.disable("test timed out")
                conn2.disable("test timed out")

    await asyncio.wait(
        [
            asyncio.create_task(run_test()),
            asyncio.create_task(conn_disabler(2.0)),
            asyncio.create_task(conn1.process()),
            asyncio.create_task(conn2.process()),
        ],
        return_when=asyncio.ALL_COMPLETED,
    )
