"""
Test the 'net.stream' module.
"""

# built-in
import asyncio

# module under test
from runtimepy.message.handlers import event_wait

# internal
from tests.resources import run_async_test


def test_event_wait_basic():
    """Test the event wait can time out."""

    assert not run_async_test(event_wait(asyncio.Event(), 0.0))
