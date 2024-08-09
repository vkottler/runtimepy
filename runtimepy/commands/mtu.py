"""
An entry-point for the 'mtu' command.
"""

# built-in
import argparse

# third-party
from vcorelib.args import CommandFunction

# internal
from runtimepy.net.mtu import UDP_DEFAULT_MTU, discover_mtu


def mtu_cmd(args: argparse.Namespace) -> int:
    """Execute the mtu command."""

    print(args.probe_size)
    print(args.fallback)

    print(discover_mtu)

    # def discover_mtu(
    #     *destination: IpHostlike,
    #     local: IpHost = None,
    #     probe_size=args.probe_size,
    #     fallback=args.fallback,
    #     kind: int = socket.SOCK_DGRAM,
    # ) -> int:

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
        default=UDP_DEFAULT_MTU,
        help="fallback MTU value if probing doesn't succeed "
        "(i.e. not on Linux, default: %(default)d)",
    )

    # udp vs tcp
    # ip6 flag?

    # dest
    # local params?

    return mtu_cmd
