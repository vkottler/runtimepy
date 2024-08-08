"""
A module implementing utilities for calculating maximum transmission-unit
sizes.
"""

# built-in
from contextlib import suppress
from enum import IntEnum
import logging
import socket

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


IP_HEADER_SIZE = 60
DEFAULT_MTU = 1500 - (IP_HEADER_SIZE + 8)


def socket_discover_mtu(sock: socket.SocketType, probe_size: int) -> int:
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
        count = sock.send(bytes(probe_size))
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

    return result if result else DEFAULT_MTU


def discover_mtu(
    *destination: IpHostlike,
    local: IpHost = None,
    probe_size: int = DEFAULT_MTU,
) -> int:
    """
    Determine the maximum transmission unit for an IPv4 payload to a provided
    host.
    """

    local = normalize_host(local)

    sock = get_free_socket(local=local, kind=socket.SOCK_DGRAM)

    dest = normalize_host(*destination)
    LOG.info(
        "Connecting MTU probe (via UDP) to %s (%s).", dest, dest.address_str
    )

    sock.connect(dest.address_str_tuple)

    result = socket_discover_mtu(sock, probe_size)

    LOG.info(
        "Discovered MTU to (%s -> %s) is %d (probe size: %d).",
        local,
        dest,
        result,
        probe_size,
    )

    sock.close()

    return result
