"""
An entry-point for the 'arbiter' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
import asyncio as _asyncio
from pathlib import Path as _Path
from typing import Optional

# third-party
from vcorelib.args import CommandFunction as _CommandFunction
from vcorelib.asyncio import run_handle_stop as _run_handle_stop

from runtimepy.commands.tui import curses_wrap_if

# internal
from runtimepy.net.arbiter import ConnectionArbiter
from runtimepy.tui.channels import CursesWindow as _CursesWindow


async def entry(
    stop_sig: _asyncio.Event, args: _Namespace, window: _CursesWindow = None
) -> int:
    """The async command entry."""

    arbiter = ConnectionArbiter(stop_sig=stop_sig, window=window)
    await arbiter.load_configs(args.configs)
    return await arbiter.app()


EXIT_CODE = 0


def app(window: Optional[_CursesWindow], args: _Namespace) -> None:
    """Start the application with an optional TUI."""

    stop_sig = _asyncio.Event()
    global EXIT_CODE  # pylint: disable=global-statement
    EXIT_CODE = _run_handle_stop(
        stop_sig, entry(stop_sig, args, window=window)
    )


def arbiter_cmd(args: _Namespace) -> int:
    """Execute the arbiter command."""

    curses_wrap_if(args.curses, app, args)
    return EXIT_CODE


def add_arbiter_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add arbiter-command arguments to its parser."""

    parser.add_argument(
        "--curses",
        action="store_true",
        help="whether or not to use curses.wrapper when starting",
    )

    parser.add_argument(
        "configs", type=_Path, nargs="+", help="the configuration to load"
    )
    return arbiter_cmd
