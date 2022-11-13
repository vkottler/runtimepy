"""
An entry-point for the 'tui' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace

# third-party
from vcorelib.args import CommandFunction as _CommandFunction


def tui_cmd(args: _Namespace) -> int:
    """Execute the tui command."""

    print(args)
    return 0


def add_tui_cmd(_: _ArgumentParser) -> _CommandFunction:
    """Add tui-command arguments to its parser."""

    return tui_cmd
