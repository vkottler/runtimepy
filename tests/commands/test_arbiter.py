"""
Test the 'commands.arbiter' module.
"""

# module under test
from runtimepy import PKG_NAME
from runtimepy.entry import main as runtimepy_main

# internal
from tests.resources import resource


def test_arbiter_command_basic():
    """Test basic usages of the 'arbiter' command."""

    assert (
        runtimepy_main(
            [
                PKG_NAME,
                "arbiter",
                str(resource("connection_arbiter", "basic.yaml")),
            ]
        )
        == 0
    )
