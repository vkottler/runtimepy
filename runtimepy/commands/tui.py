"""
An entry-point for the 'tui' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
import asyncio as _asyncio
import curses as _curses

# third-party
from vcorelib.args import CommandFunction as _CommandFunction
from vcorelib.asyncio import run_handle_interrupt as _run_handle_interrupt

from runtimepy.channel.environment import (
    ChannelEnvironment as _ChannelEnvironment,
)

# internal
from runtimepy.tui.task import TuiTask as _TuiTask


def start(window: _curses.window, _: _Namespace) -> None:
    """Start the user interface."""

    task = _TuiTask("ui", 0.01, _ChannelEnvironment())
    _run_handle_interrupt(task.run(window), _asyncio.get_event_loop())


def tui_cmd(args: _Namespace) -> int:
    """Execute the tui command."""

    _curses.wrapper(start, args)
    return 0


def add_tui_cmd(_: _ArgumentParser) -> _CommandFunction:
    """Add tui-command arguments to its parser."""

    return tui_cmd
