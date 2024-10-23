"""
Test the 'net.tcp.telnet.np_05b' module.
"""

# built-in
import asyncio

# third-party
from pytest import mark

from runtimepy.net import sockname
from runtimepy.net.arbiter import AppInfo, ConnectionArbiter
from runtimepy.net.factories import TcpConnectionFactory
from runtimepy.net.tcp.connection import TcpConnection

# module under test
from runtimepy.net.tcp.telnet.np_05b import Np05bConnection, Np05bStrings

# internal
from tests.resources import resource


class MockNp05b(TcpConnection):
    """A mocked endpoint for the NP-05B networked PDU."""

    def init(self) -> None:
        """Initialize this instance."""

        self.port_states = [False for _ in range(Np05bConnection.num_ports)]

    def port_status_str(self) -> str:
        """Get port statuses."""

        result = ""
        for port in reversed(self.port_states):
            result += "1" if port else "0"
        return result

    async def async_init(self) -> bool:
        """A runtime initialization routine (executes during 'process')."""

        # Prompt and things.
        self.send_text("Synaccess Telnet V6.2\r\n")
        self.send_text(">")

        return True

    async def process_text(self, data: str) -> bool:
        """Process a text frame."""

        for line in data.splitlines():
            if Np05bStrings.OUTLET_STATUS.value in line:
                self.send_text(f"{line}")
                self.send_text(f"$A0,{self.port_status_str()}\r\n")

            elif Np05bStrings.SET_OUTLET.value in line:
                parts = line.split(" ")

                self.send_text(f"{line}\r\n")

                real_idx = int(parts[1]) - 1

                if real_idx == 0:
                    self.port_states[real_idx] = parts[2] == "1"
                    self.send_text("$A0\r\n")

                # Arbitrarily fail to set other outlet states.
                else:
                    self.send_text("$AF\r\n")

        return True

    async def process_binary(self, data: bytes) -> bool:
        """Process a binary frame."""
        return await self.process_text(data.decode())


class MockNp05bConn(TcpConnectionFactory[MockNp05b]):
    """A connection factory for the mock NP-05B."""

    kind = MockNp05b


async def np_05b_test(app: AppInfo) -> int:
    """Test body for connection-arbiter integration test for driver."""

    client = app.single(kind=Np05bConnection)

    # Don't automatically restart the client (can cause test to hang).
    client.env.set("auto_restart", False)

    return 0


@mark.asyncio
async def test_np_05b_basic():
    """Test basic interactions with the NP-05B networked PDU."""

    # This can be used to connect to a real unit.
    # conn = await Np05bConnection.create_connection(host="pdu", port=23)

    stop_sig = asyncio.Event()

    queue: asyncio.Queue[MockNp05b] = asyncio.Queue()

    success = False

    def conn_cb(conn: MockNp05b) -> None:
        """Publish the server-side connection to the queue."""
        queue.put_nowait(conn)

    async def test_conns(client: Np05bConnection, _: MockNp05b) -> None:
        """Test NP-05B with mocked server."""

        try:
            # Wait for the client's initialization to complete.
            await client.initialized.wait()

            assert await client.set_outlet_state(0, False) is False

            assert await client.set_outlet_state(1, True) is True
            assert await client.set_outlet_state(1, True) is True
            assert await client.set_outlet_state(1, False) is True

            chan = "outlet.1.on"

            assert client.command.hooks
            assert client.command.command(f"set {chan} true")
            assert client.command.command(f"toggle {chan}")
            assert not client.outgoing_commands.empty()
            await client.process_command_queue()

            # We have instrumented this to fail.
            assert await client.set_outlet_state(2, True) is False

            # Custom commands.
            client.command.command("custom all_on")
            client.command.command("custom all_off")
            await client.process_command_queue()

            nonlocal success
            success = True
        finally:
            # End the test.
            stop_sig.set()

    async with MockNp05b.serve(
        callback=conn_cb, host="127.0.0.1", port=0
    ) as server:
        host = sockname(server.sockets[0])
        conn = await Np05bConnection.create_connection(
            host=host.name, port=host.port
        )
        conn_srv = await queue.get()

        await asyncio.wait(
            [
                asyncio.create_task(x)
                for x in [
                    test_conns(conn, conn_srv),
                    conn.process(stop_sig=stop_sig),
                    conn_srv.process(stop_sig=stop_sig),
                ]
            ],
            return_when=asyncio.ALL_COMPLETED,
        )

    assert success, "Test failed!"


@mark.asyncio
async def test_np_05b_factories():
    """
    Test basic interactions with the NP-05B networked PDU when using the
    runtimepy network-app framework.
    """

    arbiter = ConnectionArbiter()

    # Register clients and servers from the config.
    await arbiter.load_configs(
        [resource("connection_arbiter", "np_05b_test.yaml")]
    )

    assert await arbiter.app() == 0
