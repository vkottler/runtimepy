"""
Test the subprocess management interface.
"""

# built-in
import asyncio
from logging import getLogger
from pathlib import Path
from sys import executable

# third-party
from pytest import mark

# module under test
from runtimepy.subprocess import spawn_exec, spawn_shell
from runtimepy.subprocess.protocol import RuntimepySubprocessProtocol

TEST_PROGRAM = Path(__file__).parent.joinpath("program.py")
LOG = getLogger(__name__)


async def basic_proto_test(proto: RuntimepySubprocessProtocol) -> None:
    """Perform a basic input output test with a subprocess protocol."""

    proto.stdin.write("WHAT'S GOOD.".encode())

    message = await proto.stderr.get()
    assert message.decode()
    LOG.info("stderr message: %s.", message)

    message = await proto.stdout.get()
    assert message.decode()
    LOG.info("stdout message: %s.", message)


@mark.asyncio
async def test_subprocess_manager_basic():
    """Test basic interactions with the subprocess manager."""

    stdout: asyncio.Queue[bytes] = asyncio.Queue()
    stderr: asyncio.Queue[bytes] = asyncio.Queue()

    async with spawn_exec(
        executable, str(TEST_PROGRAM), stdout=stdout, stderr=stderr
    ) as proto:
        await basic_proto_test(proto)

    async with spawn_shell(
        f"{executable} {TEST_PROGRAM}", stdout=stdout, stderr=stderr
    ) as proto:
        await basic_proto_test(proto)
