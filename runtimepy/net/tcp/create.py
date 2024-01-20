"""
A module for instantiating the underlying networking resources for
TcpConnection.
"""

# built-in
import asyncio as _asyncio
from asyncio import Transport as _Transport
from logging import getLogger as _getLogger
from typing import Callable, Optional

# internal
from runtimepy.net.backoff import ExponentialBackoff
from runtimepy.net.tcp.protocol import QueueProtocol
from runtimepy.net.util import try_log_connection_error

TcpTransportProtocol = tuple[_Transport, QueueProtocol]
LOG = _getLogger(__name__)


async def tcp_transport_protocol(**kwargs) -> TcpTransportProtocol:
    """
    Create a transport and protocol pair relevant for this class's
    implementation.
    """

    transport: _Transport
    transport, protocol = await _asyncio.get_event_loop().create_connection(
        QueueProtocol, **kwargs
    )
    return transport, protocol


TcpTransportProtocolCallback = Callable[[TcpTransportProtocol], None]


async def try_tcp_transport_protocol(
    callback: TcpTransportProtocolCallback = None,
    **kwargs,
) -> Optional[TcpTransportProtocol]:
    """Attempt to create a transport and protocol pair."""

    result = await try_log_connection_error(
        tcp_transport_protocol(**kwargs),
        f"Error creating TCP connection ({kwargs}):",
        logger=LOG,
    )

    if callback is not None and result is not None:
        callback(result)

    return result


async def tcp_transport_protocol_backoff(
    backoff: ExponentialBackoff = None, **kwargs
) -> TcpTransportProtocol:
    """
    Create a transport and protocol pair relevant for this class's
    implementation.
    """

    if backoff is None:
        backoff = ExponentialBackoff()

    result = None

    while result is None and not backoff.give_up:
        await backoff.sleep()
        result = await try_tcp_transport_protocol(**kwargs)

    assert result is not None, f"Couldn't create TCP connection '{kwargs}'."
    return result
