"""
Test the 'subprocess.peer' module.
"""

# built-in
from sys import executable

# third-party
from pytest import mark

# module under test
from runtimepy.subprocess.sample import SamplePeer

# internal
from tests.subprocess.test_manager import TEST_PROGRAM


@mark.asyncio
async def test_subprocess_peer_basic():
    """Test basic interactions with the subprocess peer interface."""

    prog = TEST_PROGRAM.with_name("message_program.py")

    async with SamplePeer.shell("test", {}, f"{executable} {prog}") as peer:
        await peer.main()

    async with SamplePeer.exec("test", {}, executable, str(prog)) as peer:
        await peer.main()
