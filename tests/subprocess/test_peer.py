"""
Test the 'subprocess.peer' module.
"""

# built-in
import asyncio
from sys import executable

# third-party
from pytest import mark

# module under test
from runtimepy.net.arbiter.struct import SampleStruct
from runtimepy.subprocess.peer import RuntimepyPeer

# internal
from tests.subprocess.test_manager import TEST_PROGRAM


async def basic_peer_test(peer: RuntimepyPeer) -> None:
    """Perform a basic input output test with a subprocess protocol."""

    peer.stage_remote_log("What's good %s.", "bud")

    await peer.wait_json({"a": 1, "b": 2, "c": 3})

    await asyncio.sleep(0)


@mark.asyncio
async def test_subprocess_peer_basic():
    """Test basic interactions with the subprocess peer interface."""

    prog = TEST_PROGRAM.with_name("message_program.py")

    struct = SampleStruct("test", {})
    async with RuntimepyPeer.shell(struct, f"{executable} {prog}") as peer:
        struct.poll()
        await basic_peer_test(peer)
        struct.poll()

    struct = SampleStruct("test", {})
    async with RuntimepyPeer.exec(struct, executable, str(prog)) as peer:
        struct.poll()
        await basic_peer_test(peer)
        struct.poll()
