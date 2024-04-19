"""
Test the 'subprocess.peer' module.
"""

# built-in
import asyncio
from sys import executable

# third-party
from pytest import mark

# module under test
from runtimepy.subprocess.peer import RuntimepyPeer

# internal
from tests.subprocess.test_manager import TEST_PROGRAM


async def basic_peer_test(peer: RuntimepyPeer) -> None:
    """Perform a basic input output test with a subprocess protocol."""

    peer.stage_remote_log("What's good %s.", "bud")
    peer.send_json({"a": 1, "b": 2, "c": 3})
    await asyncio.sleep(0)


@mark.asyncio
async def test_subprocess_peer_basic():
    """Test basic interactions with the subprocess peer interface."""

    prog = TEST_PROGRAM.with_name("message_program.py")

    async with RuntimepyPeer.shell(f"{executable} {prog}") as peer:
        await basic_peer_test(peer)

    async with RuntimepyPeer.exec(executable, str(prog)) as peer:
        await basic_peer_test(peer)
