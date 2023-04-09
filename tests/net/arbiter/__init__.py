"""
Utilities for testing the connection arbiter.
"""

# module under test
from runtimepy.net.arbiter import ConnectionArbiter


def get_test_arbiter() -> ConnectionArbiter:
    """
    Get a connection arbiter with some basic connection factories registered.
    """

    arbiter = ConnectionArbiter()

    # Register connection factories.
    assert arbiter.register_module_factory(
        "tests.sample.SampleUdpConn", "udp", "sample"
    )
    assert arbiter.register_module_factory(
        "tests.sample.SampleTcpConn", "tcp", "sample"
    )
    assert arbiter.register_module_factory(
        "tests.sample.SampleWebsocketConn", "websocket", "sample"
    )

    return arbiter
