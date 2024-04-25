"""
Test the 'subprocess.peer' module.
"""

# built-in
from sys import executable

# third-party
from pytest import mark
from vcorelib.io import DEFAULT_INCLUDES_KEY

# module under test
from runtimepy.channel.environment.command import clear_env
from runtimepy.sample.peer import SamplePeer

# internal
from tests.subprocess.test_manager import TEST_PROGRAM


@mark.asyncio
async def test_subprocess_peer_basic():
    """Test basic interactions with the subprocess peer interface."""

    prog = TEST_PROGRAM.with_name("message_program.py")

    clear_env()
    async with SamplePeer.shell("test", {}, f"{executable} {prog}") as peer:
        await peer.main()

    clear_env()
    async with SamplePeer.exec("test", {}, executable, str(prog)) as peer:
        await peer.main()


@mark.asyncio
async def test_subprocess_peer_jit():
    """Test JIT script via the subprocess peer interface."""

    clear_env()
    async with SamplePeer.running_program(
        "test",
        {
            "app": "runtimepy.sample.program.run",
            "config": {"a": 100, "b": 2, "c": 3},
            DEFAULT_INCLUDES_KEY: ["package://runtimepy/server.yaml"],
        },
        "runtimepy.sample.program.SampleProgram",
    ) as peer:
        await peer.main()
