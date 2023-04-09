"""
Test the 'net.apps' module.
"""

# built-in
import asyncio

from runtimepy.net.apps import wait_for_stop

# module under test
from runtimepy.net.arbiter import ConnectionArbiter


def test_app_wait_for_stop():
    """Test the 'wait_for_stop' app method."""

    stop = asyncio.Event()
    arbiter = ConnectionArbiter(stop_sig=stop, app=wait_for_stop)

    # Just set the stop signal before the application runs.
    stop.set()
    assert arbiter.run() == 0
