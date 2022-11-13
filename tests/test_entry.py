"""
runtimepy - Test the program's entry-point.
"""

# built-in
import curses
from os import environ
from subprocess import check_output
from sys import executable, platform
from unittest.mock import patch

# module under test
from runtimepy import PKG_NAME
from runtimepy.entry import main as runtimepy_main


def test_entry_basic():
    """Test basic argument parsing."""

    args = [PKG_NAME, "noop"]
    assert runtimepy_main(args) == 0

    with patch("runtimepy.entry.entry", side_effect=SystemExit(1)):
        assert runtimepy_main(args) != 0


def test_package_entry():
    """Test the command-line entry through the 'python -m' invocation."""

    check_output([executable, "-m", "runtimepy", "-h"])


def wrapper_mock(*args, **kwargs) -> None:
    """Create a virtual window."""

    # Set some environment variables if they're not set.
    if platform in ["linux", "darwin"]:
        if "TERM" not in environ:
            environ["TERM"] = "linux"
        if "TERMINFO" not in environ:
            environ["TERMINFO"] = "/etc/terminfo"

    # Initialize the library (else curses won't work at all).
    getattr(curses, "initscr")()  # curses.initscr()
    getattr(curses, "start_color")()  # curses.start_color()

    # Send a re-size event.
    # curses.ungetch(curses.KEY_RESIZE)
    getattr(curses, "ungetch")(getattr(curses, "KEY_RESIZE"))

    # Create a virtual window for the application to use.
    window = getattr(curses, "newwin")(24, 80)  # curses.newwin(24, 80)

    args[0](window, *args[1:], **kwargs)


def test_entry_tui_cmd():
    """Test basic usages of the 'tui' command."""

    with patch("runtimepy.commands.tui._curses.wrapper", new=wrapper_mock):
        # Only run 20 iterations.
        assert runtimepy_main([PKG_NAME, "tui", "-i", "20"]) == 0
