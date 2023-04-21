"""
An entry-point for the 'arbiter' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
import asyncio as _asyncio
from pathlib import Path as _Path

# third-party
from vcorelib.args import CommandFunction as _CommandFunction
from vcorelib.asyncio import run_handle_stop as _run_handle_stop

# internal
from runtimepy.net.arbiter import ConnectionArbiter


async def entry(stop_sig: _asyncio.Event, args: _Namespace) -> int:
    """The async command entry."""

    arbiter = ConnectionArbiter(stop_sig=stop_sig)
    await arbiter.load_configs(args.configs)
    return await arbiter.app()


def arbiter_cmd(args: _Namespace) -> int:
    """Execute the arbiter command."""

    stop_sig = _asyncio.Event()
    return _run_handle_stop(stop_sig, entry(stop_sig, args))


def add_arbiter_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add arbiter-command arguments to its parser."""

    parser.add_argument(
        "configs", type=_Path, nargs="+", help="the configuration to load"
    )
    return arbiter_cmd
