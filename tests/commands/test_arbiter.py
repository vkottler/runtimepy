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
        runtimepy_main(
            base + ["-w", "--init_only", str(resource("empty.yaml"))]
        )
        == 0
    )

    apps = []
    apps.append("basic")
    apps.append("http")
    apps.append("runtimepy_http")
    for entry in apps:
        assert (
            runtimepy_main(
                base + [str(resource("connection_arbiter", f"{entry}.yaml"))]
            )
            == 0
        )
