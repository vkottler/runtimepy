"""
Test the 'commands.arbiter' module.
"""

# third-party
from pytest import mark
from vcorelib.platform import is_windows

# module under test
from runtimepy.entry import main as runtimepy_main

# internal
from tests.resources import base_args, resource


@mark.timeout(30)
def test_arbiter_command_basic():
    """Test basic usages of the 'arbiter' command."""

    base = base_args("arbiter")

    assert (
        runtimepy_main(
            base + ["-w", "--init_only", str(resource("empty.yaml"))]
        )
        == 0
    )

    for entry in ["basic", "http", "control"]:
        assert (
            runtimepy_main(
                base + [str(resource("connection_arbiter", f"{entry}.yaml"))]
            )
            == 0
        )


@mark.timeout(30)
def test_arbiter_command_advanced():
    """Test advanced usages of the 'arbiter' command."""

    base = base_args("arbiter")

    # Run with dummy load.
    for entry in ["runtimepy_http"]:
        args = base + [str(resource("connection_arbiter", f"{entry}.yaml"))]
        if not is_windows():
            args.append("dummy_load")
            args.append("browser")

        assert runtimepy_main(args) == 0
