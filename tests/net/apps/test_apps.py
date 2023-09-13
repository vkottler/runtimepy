"""
Test the 'net.apps' module.
"""

# built-in
import asyncio

# module under test
from runtimepy.net.apps import wait_for_stop
from runtimepy.net.arbiter import ConnectionArbiter

# internal
from tests.resources import can_use_uvloop


def test_app_wait_for_stop():
    """Test the 'wait_for_stop' app method."""

    stop = asyncio.Event()
    arbiter = ConnectionArbiter(stop_sig=stop, app=wait_for_stop)

    # Just set the stop signal before the application runs.
    stop.set()
    assert arbiter.run(enable_uvloop=can_use_uvloop()) == 0
