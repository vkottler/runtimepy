"""
An entry-point for the 'tui' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
import asyncio as _asyncio
import curses as _curses
from typing import Optional

# third-party
from vcorelib.args import CommandFunction as _CommandFunction
from vcorelib.asyncio import run_handle_stop as _run_handle_stop

# internal
from runtimepy.channel.environment import (
    ChannelEnvironment as _ChannelEnvironment,
)
from runtimepy.tui.channels import CursesWindow as _CursesWindow
from runtimepy.tui.task import TuiTask as _TuiTask


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
        enable_uvloop=not getattr(args, "no_uvloop", False),
    )

    return 0


def curses_wrap_if(method: _CommandFunction, args: _Namespace) -> int:
    """Run a method in TUI mode if a condition is met."""

    assert not hasattr(args, "window"), args
    args.window = None

    result = -1

    if getattr(args, "curses", False):

        def wrapper(window: Optional[_CursesWindow], args: _Namespace) -> None:
            """Set the window attribute."""

            args.window = window
            nonlocal result
            result = method(args)

        getattr(_curses, "wrapper")(wrapper, args)
    else:
        result = method(args)

    return result


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
