"""
Test the 'util' module.
"""

# third-party
from pytest import mark

# module under test
from runtimepy.util import read_binary

# internal
from tests.resources import resource


@mark.asyncio
async def test_read_binary():
    """Test 'read_binary' invocations."""

    assert await read_binary(resource("test.txt"))
