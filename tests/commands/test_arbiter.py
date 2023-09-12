"""
Test the 'commands.arbiter' module.
"""

# module under test
from runtimepy.entry import main as runtimepy_main

# internal
from tests.resources import base_args, resource


def test_arbiter_command_basic():
    """Test basic usages of the 'arbiter' command."""

    base = base_args("arbiter")

    assert (
        runtimepy_main(base + ["--init_only", str(resource("empty.yaml"))])
        == 0
    )

    for entry in ["basic.yaml"]:
        assert (
            runtimepy_main(base + [str(resource("connection_arbiter", entry))])
            == 0
        )
