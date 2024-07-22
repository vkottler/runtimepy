"""
Test the 'commands.tftp' module.
"""

# built-in
from pathlib import Path
from tempfile import TemporaryDirectory

# third-party
from vcorelib import DEFAULT_ENCODING

# module under test
from runtimepy.entry import main as runtimepy_main

# internal
from tests.resources import base_args


def test_tftp_command_basic():
    """Test basic usages of the 'tftp' command."""

    base = base_args("tftp", "-t", "0.0", "-r", "0.0")

    with TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        ours = tmp.joinpath("a.txt")
        with ours.open("w", encoding=DEFAULT_ENCODING) as path_fd:
            path_fd.write("Hello, world!\n")

        theirs = tmp.joinpath("b.txt")
        with theirs.open("w", encoding=DEFAULT_ENCODING) as path_fd:
            path_fd.write("Hello, world!\n")

        runtimepy_main(base + ["write", "localhost", str(ours), str(theirs)])
        runtimepy_main(base + ["read", "localhost", str(ours)])
