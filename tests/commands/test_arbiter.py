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
            [PKG_NAME, "arbiter", "--init_only", str(resource("empty.yaml"))]
        )
        == 0
    )

    for entry in ["basic.yaml"]:
        assert (
            runtimepy_main(
                [
                    PKG_NAME,
                    "arbiter",
                    str(resource("connection_arbiter", entry)),
                ]
            )
            == 0
        )
