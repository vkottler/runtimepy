# =====================================
# generator=datazen
# version=3.1.3
# hash=70b70e2522b648c99a1b710278c8f242
# =====================================

"""
This package's command-line entry-point (boilerplate).
"""

# built-in
import argparse
import logging
import os
from pathlib import Path
import sys
from typing import List

# internal
from runtimepy import DESCRIPTION, VERSION
from runtimepy.app import add_app_args, entry


def init_logging(args: argparse.Namespace) -> None:
    """Initialize logging based on command-line arguments."""

    if not getattr(args, "curses", False):
        logging.basicConfig(
            level=logging.DEBUG if args.verbose else logging.INFO,
            format="%(name)-36s - %(levelname)-6s - %(message)s",
        )


def main(argv: List[str] = None) -> int:
    """Program entry-point."""

    result = 0

    # fall back on command-line arguments
    command_args = sys.argv
    if argv is not None:
        command_args = argv

    # initialize argument parsing
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="set to increase logging verbosity",
    )
    parser.add_argument(
        "--curses",
        action="store_true",
        help="whether or not to use curses.wrapper when starting",
    )
    parser.add_argument(
        "-C",
        "--dir",
        default=Path.cwd(),
        dest="dir",
        type=Path,
        help="execute from a specific directory",
    )
    starting_dir = Path.cwd()

    add_app_args(parser)

    # parse arguments and execute the requested command
    try:
        args = parser.parse_args(command_args[1:])
        args.version = VERSION
        args.dir = args.dir.resolve()

        # initialize logging
        init_logging(args)

        # change to the specified directory
        os.chdir(args.dir)

        # run the application
        result = entry(args)
    except SystemExit as exc:
        result = 1
        if exc.code is not None and isinstance(exc.code, int):
            result = exc.code

    # return to starting dir
    os.chdir(starting_dir)

    return result
