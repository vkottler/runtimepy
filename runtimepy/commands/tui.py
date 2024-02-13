"""
An entry-point for the 'tui' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
import asyncio as _asyncio

# third-party
from vcorelib.args import CommandFunction as _CommandFunction
from vcorelib.asyncio import run_handle_stop as _run_handle_stop

from runtimepy.channel.environment import (
    ChannelEnvironment as _ChannelEnvironment,
)

# internal
from runtimepy.commands.common import curses_wrap_if
from runtimepy.tui.task import TuiTask as _TuiTask

__all__ = ("curses_wrap_if", "start", "tui_cmd", "add_tui_cmd")


def start(args: _Namespace) -> int:
    """Start the user interface."""

    assert args.window is not None

    task = _TuiTask(
        "ui",
        1 / args.rate,
        _ChannelEnvironment(),
        max_iterations=args.iterations,
    )

    stop_sig = _asyncio.Event()
    _run_handle_stop(
        stop_sig,
        task.run(
            args.window,
            stop_sig=stop_sig,
        ),
        eloop=_asyncio.new_event_loop(),
        enable_uvloop=not getattr(args, "no_uvloop", False),
    )

    return 0


def tui_cmd(args: _Namespace) -> int:
    """Execute the tui command."""

    args.curses = True
    return curses_wrap_if(start, args)


def add_tui_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add tui-command arguments to its parser."""

    parser.add_argument(
        "-i",
        "--iterations",
        type=int,
        default=0,
        help=(
            "maximum number of program iterations (if greater "
            "than zero, default: %(default)s)"
        ),
    )
    parser.add_argument(
        "-r",
        "--rate",
        type=float,
        default=60.0,
        help=(
            "frequency (in Hz) to run the interface "
            "(default: %(default)s Hz)"
        ),
    )
    return tui_cmd
