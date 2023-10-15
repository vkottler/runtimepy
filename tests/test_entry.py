"""
runtimepy - Test the program's entry-point.
"""

# built-in
import importlib
from subprocess import check_output
from sys import executable
from unittest.mock import patch

# module under test
from runtimepy import PKG_NAME
from runtimepy.entry import main as runtimepy_main
from runtimepy.tui.mock import wrapper_mock

# internal
from tests.resources import base_args


def test_entry_basic():
    """Test basic argument parsing."""

    args = [PKG_NAME, "noop"]
    assert runtimepy_main(args) == 0

    with patch("runtimepy.entry.entry", side_effect=SystemExit(1)):
        assert runtimepy_main(args) != 0


def test_package_entry():
    """Test the command-line entry through the 'python -m' invocation."""

    check_output([executable, "-m", "runtimepy", "-h"])


def test_entry_tui_cmd():
    """Test basic usages of the 'tui' command."""

    try:
        # Only run these tests if the curses module is present.
        importlib.import_module("curses")
        base = base_args("tui")

        with patch(
            "runtimepy.commands.common._curses.wrapper", new=wrapper_mock
        ):
            # Only run 20 iterations.
            assert runtimepy_main(base + ["-i", "20"]) == 0
    except ModuleNotFoundError:
        pass
