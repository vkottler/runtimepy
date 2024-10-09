"""
Test the 'commands.server' module.
"""

# module under test
from runtimepy.entry import main as runtimepy_main

# internal
from tests.resources import base_args, resource


def test_server_command_basic():
    """Test basic usages of the 'server' command."""

    base = base_args("server")
    assert runtimepy_main(base + ["-l", "tcp_null"]) == 0
    assert runtimepy_main(base + ["-l", "websocket_null"]) == 0
    assert runtimepy_main(base + ["-u", "-l", "udp_null"]) == 0

    assert (
        runtimepy_main(
            base
            + [
                "-l",
                "--certfile",
                str(resource("certs", "test.cert")),
                "--keyfile",
                str(resource("certs", "test.key")),
                "tcp_null",
            ]
        )
        == 0
    )
