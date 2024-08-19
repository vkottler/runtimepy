"""
Test the 'commands.mtu' module.
"""

# module under test
from runtimepy.entry import main as runtimepy_main

# internal
from tests.resources import base_args


def test_mtu_command_basic():
    """Test basic usages of the 'mtu' command."""

    base = base_args("mtu")
    assert runtimepy_main(base + ["localhost", "8000"]) == 0
    assert runtimepy_main(base + ["::1", "8000", "0", "0"]) == 0
