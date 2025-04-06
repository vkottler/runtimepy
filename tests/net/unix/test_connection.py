"""
Test the 'net.unix' module.
"""

# built-in
import asyncio
from logging import getLogger
import socket

# third-party
from pytest import mark
from vcorelib.io.fifo import ByteFifo
from vcorelib.platform import is_windows

LOG = getLogger()


def abstract_socket_name(name: str) -> bytes:
    """Get bytes to use as a unix socket name."""

    fifo = ByteFifo()
    fifo.ingest(bytes(1))
    fifo.ingest(name.encode())
    result = fifo.pop(fifo.size)
    assert result
    return result


def unix_socket(
    path: str | bytes,
    kind: int = socket.SOCK_DGRAM,
    proto: int = 0,
    fileno: int = None,
) -> socket.socket:
    """Create a unix socket bound to path."""

    sock = socket.socket(
        family=socket.AF_UNIX,
        type=kind | socket.SOCK_NONBLOCK,
        proto=proto,
        fileno=fileno,
    )

    sock.bind(path)

    return sock


@mark.asyncio
async def test_unix_basic():
    """Test basic unix socket interactions."""

    if is_windows():
        return

    class SampleProtocol(asyncio.DatagramProtocol):
        """Used for dev testing."""

        def datagram_received(self, data, addr) -> None:
            """TODO."""
            LOG.info("data: %s, %s", data, addr)

        def error_received(self, exc) -> None:
            """TODO."""
            LOG.exception("error_received:", exc_info=exc)

        def connection_made(self, transport) -> None:
            """Save the transport reference and notify."""
            LOG.info("CONNECTION MADE %s", transport)

    path1 = abstract_socket_name("path1")
    path2 = abstract_socket_name("path2")
    sock1 = unix_socket(path1)
    sock2 = unix_socket(path2)
    sock1.connect(path2)
    sock2.connect(path1)

    loop = asyncio.get_running_loop()

    (transport1, protocol1) = await loop.create_datagram_endpoint(
        SampleProtocol, sock=sock1
    )

    (transport2, protocol2) = await loop.create_datagram_endpoint(
        SampleProtocol, sock=sock2
    )

    del protocol1
    del protocol2

    transport1.sendto("hello, world! (1)".encode())
    transport2.sendto("hello, world! (2)".encode())

    LOG.info(transport1)
    LOG.info(transport2)

    await asyncio.sleep(5)

    transport1.close()
    transport2.close()
