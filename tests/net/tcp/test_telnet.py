"""
Test the 'net.tcp.telnet' module.
"""

# built-in
import asyncio

# third-party
from pytest import mark

# module under test
from runtimepy.net.tcp.telnet import (
    NEWLINE,
    BasicTelnet,
    TelnetCode,
    TelnetNvt,
)


@mark.asyncio
async def test_telnet_connection_basic():
    """Test basic interactions with a telnet connection pair."""

    async with BasicTelnet.create_pair(peer=BasicTelnet) as (server, client):

        async def run_test() -> None:
            """
            Ensure each side of the connection is being processed to give a
            chance for messages to be processed.
            """

            server.send_text("Hello, world!")
            server.send_binary(NEWLINE)
            client.send_text("Hello, world!")
            client.send_binary(NEWLINE)

            server.send_option(TelnetCode.DO, 100)
            client.send_option(TelnetCode.WILL, 100)

            server.send_binary(bytes([TelnetNvt.BEL]))
            client.send_binary(bytes([TelnetNvt.BEL]))

            # Ensure these messages get sent.
            await asyncio.sleep(0.1)

            server.send_binary(bytes([TelnetCode.IAC, TelnetCode.IAC]))
            client.send_binary(bytes([TelnetCode.IAC, TelnetCode.IAC]))

            server.send_command(TelnetCode.IP)
            client.send_command(TelnetCode.IP)

        async def conn_disabler(
            timeout: float, poll_period: float = 0.05
        ) -> None:
            """Disable the connections after some timeout."""

            total_time = 0.0
            while not server.disabled or not client.disabled:
                await asyncio.sleep(poll_period)
                total_time += poll_period

                if total_time >= timeout:
                    server.disable("test timed out")
                    client.disable("test timed out")

        await asyncio.wait(
            [
                asyncio.create_task(run_test()),
                asyncio.create_task(conn_disabler(2.0)),
                asyncio.create_task(server.process()),
                asyncio.create_task(client.process()),
            ],
            return_when=asyncio.ALL_COMPLETED,
        )
