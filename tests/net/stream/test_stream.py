"""
Test the 'net.stream' module.
"""

# built-in
import asyncio

# third-party
from pytest import mark

# module under test
from runtimepy.net.stream.json import event_wait


@mark.asyncio
async def test_event_wait_basic():
    """Test the event wait can time out."""

    event = asyncio.Event()
    assert not await event_wait(event, 0.0)
