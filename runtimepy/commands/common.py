"""
A module for package command-line argument interfaces.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace

# third-party
from vcorelib.args import CommandFunction as _CommandFunction

try:
    import curses as _curses
except ModuleNotFoundError:  # pragma: nocover
    _curses = {}  # type: ignore


def arbiter_flags(parser: _ArgumentParser) -> None:
    """Add arbiter command-line flag arguments."""

    parser.add_argument(
        "-i",
        "--init_only",
        "--init-only",
        action="store_true",
        help="exit after completing initialization",
    )
    parser.add_argument(
        "-w",
        "--wait-for-stop",
        "--wait_for_stop",
        action="store_true",
        help="ensure that a 'wait_for_stop' application method is run last",
    )


def curses_wrap_if(method: _CommandFunction, args: _Namespace) -> int:
    """Run a method in TUI mode if a condition is met."""

    assert not hasattr(args, "window"), args
    args.window = None

    result = -1

    if getattr(args, "curses", False):

        def wrapper(window, args: _Namespace) -> None:
            """Set the window attribute."""

            args.window = window
            nonlocal result
            result = method(args)

        getattr(_curses, "wrapper")(wrapper, args)
    else:
        result = method(args)

    return result


def arbiter_args(parser: _ArgumentParser, nargs: str = "+") -> None:
    """Add common connection-arbiter parameters.."""

    arbiter_flags(parser)
    parser.add_argument(
        "configs", nargs=nargs, help="the configuration to load"
    )
