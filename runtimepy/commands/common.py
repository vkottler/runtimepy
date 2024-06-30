"""
A module for package command-line argument interfaces.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
from contextlib import contextmanager, suppress
from typing import Any, Iterator

# third-party
from vcorelib.args import CommandFunction as _CommandFunction
from vcorelib.io import ARBITER
from vcorelib.paths.context import tempfile

# internal
from runtimepy import DEFAULT_EXT, PKG_NAME

_curses = {}  # type: ignore
with suppress(ModuleNotFoundError):
    import curses as _curses  # type: ignore

FACTORIES = f"package://{PKG_NAME}/factories.{DEFAULT_EXT}"


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
    parser.add_argument(
        "--no-poller",
        action="store_true",
        help="don't run a connection-metrics poller task",
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


@contextmanager
def arbiter_args(parser: _ArgumentParser, nargs: str = "+") -> Iterator[None]:
    """Add common connection-arbiter parameters."""

    arbiter_flags(parser)
    yield
    parser.add_argument(
        "configs", nargs=nargs, help="the configuration to load"
    )


def cmd_with_jit(
    command: _CommandFunction, args: _Namespace, data: dict[str, Any]
) -> int:
    """Run an 'arbiter' command with custom data inserted."""

    with tempfile(suffix=f".{DEFAULT_EXT}") as temp_config:
        ARBITER.encode(temp_config, data)
        args.configs.append(str(temp_config))
        return command(args)
