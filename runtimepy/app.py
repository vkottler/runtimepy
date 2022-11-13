# =====================================
# generator=datazen
# version=3.1.0
# hash=7038f171453cc0bbd31445328204ecac
# =====================================

"""
This package's command-line entry-point application.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace

# third-party
from vcorelib.args import CommandFunction as _CommandFunction
from vcorelib.args import app_args as _app_args

# internal
from runtimepy.commands.all import commands

COMMAND: _CommandFunction = lambda _: 1


def entry(args: _Namespace) -> int:
    """Execute the requested task."""
    return COMMAND(args)


def add_app_args(parser: _ArgumentParser) -> None:
    """Add application-specific arguments to the command-line parser."""
    global COMMAND  # pylint: disable=global-statement
    add, COMMAND = _app_args(commands, {})
    add(parser)
