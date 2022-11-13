"""
runtimepy - Test the program's entry-point.
"""

# built-in
from subprocess import check_output
from sys import executable
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


def test_entry_tui_cmd():
    """Test basic usages of the 'tui' command."""

    assert runtimepy_main([PKG_NAME, "tui"]) == 0
