"""
An entry-point for the 'tftp' command.
"""

# built-in
import argparse
import asyncio
from pathlib import Path

# third-party
from vcorelib.args import CommandFunction
from vcorelib.asyncio import run_handle_stop

# internal
from runtimepy.net.udp.tftp import TFTP_PORT, tftp_read, tftp_write
from runtimepy.net.udp.tftp.base import DEFAULT_TIMEOUT_S, REEMIT_PERIOD_S
from runtimepy.net.udp.tftp.enums import DEFAULT_MODE
from runtimepy.net.util import normalize_host


def tftp_cmd(args: argparse.Namespace) -> int:
    """Execute the tftp command."""

    host = normalize_host(args.host, args.port)

    # Resolve hostname as early as possible.
    addr = host.address_str_tuple

    stop_sig = asyncio.Event()
    kwargs = {
        "mode": args.mode,
        "timeout_s": args.timeout,
        "reemit_period_s": args.reemit,
        "process_kwargs": {"stop_sig": stop_sig},
    }

    if not args.their_file:
        args.their_file = str(args.our_file)

    if args.operation == "read":
        task = tftp_read(addr, args.our_file, args.their_file, **kwargs)
    else:
        task = tftp_write(addr, args.our_file, args.their_file, **kwargs)

    return run_handle_stop(
        stop_sig, task, enable_uvloop=not getattr(args, "no_uvloop", False)
    )


def add_tftp_cmd(parser: argparse.ArgumentParser) -> CommandFunction:
    """Add tftp-command arguments to its parser."""

    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=TFTP_PORT,
        help="port to message (default: %(default)s)",
    )

    parser.add_argument(
        "-m",
        "--mode",
        default=DEFAULT_MODE,
        help="tftp mode to use (default: %(default)s)",
    )

    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_S,
        help="timeout for each step",
    )
    parser.add_argument(
        "-r",
        "--reemit",
        type=float,
        default=REEMIT_PERIOD_S,
        help="transmit period for each step",
    )

    parser.add_argument(
        "operation", choices=["read", "write"], help="action to perform"
    )

    parser.add_argument("host", help="host to message")

    parser.add_argument("our_file", type=Path, help="path to our file")
    parser.add_argument("their_file", nargs="?", help="path to their file")

    return tftp_cmd
