"""
An entry-point for the 'arbiter' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
import asyncio as _asyncio

# third-party
from vcorelib.args import CommandFunction as _CommandFunction
from vcorelib.asyncio import run_handle_stop as _run_handle_stop

# internal
from runtimepy.commands.common import arbiter_args
from runtimepy.commands.tui import curses_wrap_if
from runtimepy.net.arbiter import ConnectionArbiter
from runtimepy.tui.channels import CursesWindow as _CursesWindow


async def entry(
    stop_sig: _asyncio.Event, args: _Namespace, window: _CursesWindow = None
) -> int:
    """The async command entry."""

    arbiter = ConnectionArbiter(stop_sig=stop_sig, window=window)
    await arbiter.load_configs(args.configs)
    return await arbiter.app()


def app(args: _Namespace) -> int:
    """Start the application with an optional TUI."""

    stop_sig = _asyncio.Event()

    if args.init_only:
        stop_sig.set()

    return _run_handle_stop(
        stop_sig,
        entry(stop_sig, args, window=args.window),
        enable_uvloop=not getattr(args, "no_uvloop", False),
    )


def arbiter_cmd(args: _Namespace) -> int:
    """Execute the arbiter command."""

    return curses_wrap_if(app, args)


def add_arbiter_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add arbiter-command arguments to its parser."""

    arbiter_args(parser)
    return arbiter_cmd
