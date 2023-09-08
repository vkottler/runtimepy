"""
A module for package command-line argument interfaces.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser


def arbiter_args(parser: _ArgumentParser, nargs: str = "+") -> None:
    """Add common connection-arbiter parameters.."""

    parser.add_argument(
        "--init_only",
        action="store_true",
        help="exit after completing initialization",
    )
    parser.add_argument(
        "configs", nargs=nargs, help="the configuration to load"
    )
