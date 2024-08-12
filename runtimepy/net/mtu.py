"""
A module implementing utilities for calculating maximum transmission-unit
sizes.
"""

# built-in
from contextlib import suppress
from enum import IntEnum
from functools import cache
import logging
import socket
from typing import Callable

# internal
from runtimepy.net.util import (
    IpHost,
    IpHostlike,
    get_free_socket,
    normalize_host,
)

LOG = logging.getLogger(__name__)


class SocketConstants(IntEnum):
    """Some platform definitions necessary for mtu discovery."""

    IP_MTU = 14
    IP_MTU_DISCOVER = 10
    IP_PMTUDISC_DO = 2


ETHERNET_MTU = 1500
IP_HEADER_SIZE = 60
UDP_HEADER_SIZE = IP_HEADER_SIZE + 8
UDP_DEFAULT_MTU = ETHERNET_MTU - UDP_HEADER_SIZE


def socket_discover_mtu(
    sock: socket.SocketType,
    probe_size: int,
    fallback: int,
    probe_create: Callable[[int], bytes] = bytes,
) -> int:
    """
    Send a large frame and indicate that we want to perform mtu discovery, and
    not fragment any frames.
    """

    orig_val = None

    # see ip(7), force the don't-fragment flag and perform mtu discovery
    # such that the socket object can be queried for actual mtu upon error

    # Suppress platform incompatibility errors.
    with suppress(OSError):
        orig_val = sock.getsockopt(
            socket.IPPROTO_IP, SocketConstants.IP_MTU_DISCOVER
        )

    with suppress(OSError):
        sock.setsockopt(
            socket.IPPROTO_IP,
            SocketConstants.IP_MTU_DISCOVER,
            SocketConstants.IP_PMTUDISC_DO,
        )

    try:
        count = sock.send(probe_create(probe_size))
        LOG.info("mtu probe successfully sent %d bytes", count)
    except OSError as exc:
        LOG.exception(
            "Error sending %d-byte MTU probe payload:",
            probe_size,
            exc_info=exc,
        )

    # Restore the original value.
    if orig_val is not None:
        with suppress(OSError):
            sock.setsockopt(
                socket.IPPROTO_IP, SocketConstants.IP_MTU_DISCOVER, orig_val
            )

    result = 0

    # Suppress platform incompatibility errors.
    with suppress(OSError):
        result = sock.getsockopt(socket.IPPROTO_IP, SocketConstants.IP_MTU)

    return result if result else fallback


@cache
def host_discover_mtu(
    local: IpHost,
    destination: IpHost,
    probe_size: int,
    fallback: int,
    kind: int = socket.SOCK_DGRAM,
    probe_create: Callable[[int], bytes] = bytes,
) -> int:
    """Perform MTU discovery given a local and remote host plus probe size."""

    sock = get_free_socket(local=local.zero_port(), kind=kind)
    sock.connect(destination.address_str_tuple)
    result = socket_discover_mtu(
        sock, probe_size, fallback, probe_create=probe_create
    )
    sock.close()
    return result


def discover_mtu(
    *destination: IpHostlike,
    local: IpHost = None,
    probe_size: int = UDP_DEFAULT_MTU,
    fallback: int = ETHERNET_MTU,
    kind: int = socket.SOCK_DGRAM,
    probe_create: Callable[[int], bytes] = bytes,
) -> int:
    """
    Determine the maximum transmission unit for an IPv4 payload to a provided
    host.
    """

    dest = normalize_host(*destination)
    local = normalize_host(local, default=type(dest))
    result = host_discover_mtu(
        local, dest, probe_size, fallback, kind=kind, probe_create=probe_create
    )

    LOG.info(
        "Discovered MTU to (%s -> %s) is %d (probe size: %d).",
        local,
        dest,
        result,
        probe_size,
    )

    return result
