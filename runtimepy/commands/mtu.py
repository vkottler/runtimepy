"""
An entry-point for the 'mtu' command.
"""

# built-in
import argparse
import socket

# third-party
from vcorelib.args import CommandFunction

# internal
from runtimepy.net.mtu import ETHERNET_MTU, UDP_DEFAULT_MTU, discover_mtu


def mtu_cmd(args: argparse.Namespace) -> int:
    """Execute the mtu command."""

    discover_mtu(
        args.destination[0],
        *(int(x) for x in args.destination[1:]),
        probe_size=args.probe_size,
        fallback=args.fallback,
        kind=socket.SOCK_STREAM if args.tcp else socket.SOCK_DGRAM,
    )

    return 0


def add_mtu_cmd(parser: argparse.ArgumentParser) -> CommandFunction:
    """Add mtu-command arguments to its parser."""

    parser.add_argument(
        "--probe-size",
        type=int,
        default=UDP_DEFAULT_MTU,
        help="data payload size to use for probe (default: %(default)d)",
    )
    parser.add_argument(
        "--fallback",
        type=int,
        default=ETHERNET_MTU,
        help="fallback MTU value if probing doesn't succeed "
        "(i.e. not on Linux, default: %(default)d)",
    )

    parser.add_argument(
        "-t", "--tcp", action="store_true", help="use TCP instead of UDP"
    )

    parser.add_argument(
        "destination",
        nargs="+",
        help="endpoint parameters (host, port[, flowinfo, scope_id])",
    )

    return mtu_cmd
