"""
A module for instantiating the underlying networking resources for
UdpConnection.
"""

# built-in
import asyncio as _asyncio
from asyncio import DatagramTransport as _DatagramTransport
from logging import getLogger as _getLogger
from typing import Callable, Optional

# internal
from runtimepy.net.backoff import ExponentialBackoff
from runtimepy.net.udp.protocol import UdpQueueProtocol
from runtimepy.net.util import try_log_connection_error

UdpTransportProtocol = tuple[_DatagramTransport, UdpQueueProtocol]
LOG = _getLogger(__name__)


async def udp_transport_protocol(**kwargs) -> UdpTransportProtocol:
    """
    Create a transport and protocol pair relevant for this class's
    implementation.
    """

    transport: _DatagramTransport
    (
        transport,
        protocol,
    ) = await _asyncio.get_event_loop().create_datagram_endpoint(
        UdpQueueProtocol, **kwargs
    )

    return transport, protocol


UdpTransportProtocolCallback = Callable[[UdpTransportProtocol], None]


async def try_udp_transport_protocol(
    callback: UdpTransportProtocolCallback = None,
    **kwargs,
) -> Optional[UdpTransportProtocol]:
    """Attempt to create a transport and protocol pair."""

    result = await try_log_connection_error(
        udp_transport_protocol(**kwargs),
        "Error creating UDP endpoint:",
        logger=LOG,
    )

    if callback is not None and result is not None:
        callback(result)

    return result


async def udp_transport_protocol_backoff(
    backoff: ExponentialBackoff = None,
    **kwargs,
) -> UdpTransportProtocol:
    """
    Create a transport and protocol pair relevant for this class's
    implementation.
    """

    if backoff is None:
        backoff = ExponentialBackoff()

    result = None

    while result is None and not backoff.give_up:
        await backoff.sleep()
        result = await try_udp_transport_protocol(**kwargs)

    assert result is not None, f"Couldn't create UDP connection '{kwargs}'."
    return result
