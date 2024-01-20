"""
Test the 'commands.server' module.
"""

# module under test
from runtimepy.entry import main as runtimepy_main

# internal
from tests.resources import base_args


def test_server_command_basic():
    """Test basic usages of the 'server' command."""

    base = base_args("server")

    assert runtimepy_main(base + ["--init_only", "tcp_null"]) == 0
