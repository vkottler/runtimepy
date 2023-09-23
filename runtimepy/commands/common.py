"""
A module for package command-line argument interfaces.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser


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


def arbiter_args(parser: _ArgumentParser, nargs: str = "+") -> None:
    """Add common connection-arbiter parameters.."""

    arbiter_flags(parser)
    parser.add_argument(
        "configs", nargs=nargs, help="the configuration to load"
    )
