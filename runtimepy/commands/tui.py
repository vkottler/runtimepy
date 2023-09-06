"""
An entry-point for the 'tui' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
import asyncio as _asyncio
import curses as _curses
from typing import Callable, Optional

# third-party
from vcorelib.args import CommandFunction as _CommandFunction
from vcorelib.asyncio import run_handle_stop as _run_handle_stop

# internal
from runtimepy.channel.environment import (
    ChannelEnvironment as _ChannelEnvironment,
)
from runtimepy.tui.channels import CursesWindow as _CursesWindow
from runtimepy.tui.task import TuiTask as _TuiTask

CursesApp = Callable[[Optional[_CursesWindow], _Namespace], None]


def start(window: Optional[_CursesWindow], args: _Namespace) -> None:
    """Start the user interface."""

    assert window is not None

    task = _TuiTask(
        "ui",
        1 / args.rate,
        _ChannelEnvironment(),
        max_iterations=args.iterations,
    )
    stop_sig = _asyncio.Event()
    return _run_handle_stop(stop_sig, task.run(window, stop_sig=stop_sig))


def curses_wrap_if(cond: bool, method: CursesApp, args: _Namespace) -> None:
    """Run a method in TUI mode if a condition is met."""

    if cond:
        getattr(_curses, "wrapper")(method, args)
    else:
        method(None, args)


def tui_cmd(args: _Namespace) -> int:
    """Execute the tui command."""

    curses_wrap_if(True, start, args)
    return 0


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
