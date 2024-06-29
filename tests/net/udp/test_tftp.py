"""
Test the 'net.udp.tftp' module.
"""

# built-in
import asyncio
from pathlib import Path
from random import randbytes
import stat
from tempfile import TemporaryDirectory
from typing import Iterator

# third-party
from pytest import mark
from vcorelib.paths.hashing import bytes_md5_hex, file_md5_hex
from vcorelib.platform import is_windows

# module under test
from runtimepy.net.udp.tftp import TftpConnection
from runtimepy.primitives import Uint16


async def tftp_test(conn1: TftpConnection, conn2: TftpConnection) -> None:
    """Test a tftp connection pair."""

    # Classic underlying Windows bug (connected sockets should
    # "just work" but don't).
    addr = conn2.local_address if is_windows() else None

    # Send a non-sensical opcode.
    conn1.sendto(bytes(Uint16(99)), addr=addr)

    # Send every message type.
    conn1.send_ack(1, addr=addr)
    conn1.send_data(1, "Hello, world!".encode(), addr=addr)
    conn1.send_wrq("test_file", addr=addr)
    conn1.send_rrq("test_file", addr=addr)

    await asyncio.sleep(0.01)


def sample_messages() -> Iterator[bytes]:
    """Get sample file-data payloads for testing."""

    yield "Hello, world!\n".encode()
    yield randbytes(1000)
    yield randbytes(1 * 1024 * 1024)


def clear_read(path: Path) -> None:
    """Clear read bits on a file."""

    mode = path.stat().st_mode
    mode &= ~(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    path.chmod(mode)


def clear_write(path: Path) -> None:
    """Clear write bits on a file."""

    mode = path.stat().st_mode
    mode &= ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
    path.chmod(mode)


async def tftp_file_read(
    conn1: TftpConnection,
    conn2: TftpConnection,
) -> None:
    """Test a tftp connection pair."""

    fstr = "test_{}.txt"
    src_name = fstr.format("src")
    src = conn1.path.joinpath(src_name)
    dst = conn2.path.joinpath(fstr.format("dst"))

    # Classic underlying Windows bug (connected sockets should
    # "just work" but don't).
    addr = conn1.local_address if is_windows() else None

    for msg in sample_messages():
        # Write and verify.
        with src.open("wb") as path_fd:
            path_fd.write(msg)
        assert bytes_md5_hex(msg) == file_md5_hex(src)

        # Request file.
        assert await conn2.request_read(dst, src_name, addr=addr)

        # Wait for the other end of the connection to finish.
        async with conn1.endpoint().lock:
            pass

        # Compare file results.
        assert file_md5_hex(src) == file_md5_hex(dst)

    assert not await conn2.request_read(dst, "asdf.txt", addr=addr)

    # Create a file, mess with permissions, trigger no read permission.
    path = conn1.path.joinpath("test.txt")
    with path.open("wb") as path_fd:
        path_fd.write("Hello, world!\n".encode())
    clear_read(path)

    # Permission mechanism doesn't seem to work on Windows?
    assert (
        not await conn2.request_read(dst, "test.txt", addr=addr)
        or is_windows()
    )

    async with conn1.endpoint().lock:
        pass


async def tftp_file_write(
    conn1: TftpConnection, conn2: TftpConnection
) -> None:
    """Test a tftp connection pair."""

    dst_name = "dst.txt"
    src = conn1.path.joinpath("src.txt")
    dst = conn1.path.joinpath(dst_name)

    # Classic underlying Windows bug (connected sockets should
    # "just work" but don't).
    addr = conn1.local_address if is_windows() else None

    # Some simple write scenarios.
    for msg in sample_messages():
        with src.open("wb") as path_fd:
            path_fd.write(msg)

        # Write and verify.
        assert await conn2.request_write(src, dst_name, addr=addr)
        async with conn1.endpoint().lock:
            pass
        assert bytes_md5_hex(msg) == file_md5_hex(dst)

    # No write permission.
    with dst.open("wb") as path_fd:
        path_fd.write("Hello, world!\n".encode())
    clear_write(dst)
    assert not await conn2.request_write(src, dst_name, addr=addr)


@mark.asyncio
async def test_tftp_connection_basic():
    """Test basic tftp connection interactions."""

    for testcase in [tftp_file_read, tftp_file_write, tftp_test]:
        # Start connections.
        conn1, conn2 = await TftpConnection.create_pair()
        stop = asyncio.Event()
        tasks = [
            asyncio.create_task(conn1.process(stop_sig=stop)),
            asyncio.create_task(conn2.process(stop_sig=stop)),
        ]

        # Test connection.
        with TemporaryDirectory() as tmpdir:
            # Set path.
            path = Path(tmpdir)
            conn1.endpoint()
            conn1.set_root(path)
            conn2.set_root(path)

            # Set timing parameters.
            conn1.endpoint().period = 0.01
            conn1.endpoint().timeout = 0.1
            await testcase(conn1, conn2)

        # Allow connection(s) to read.
        await asyncio.sleep(0)

        # End test.
        stop.set()
        for task in tasks:
            await task

        # Clean up connection tasks.
        for task in list(conn1.tasks) + list(conn2.tasks):
            task.cancel()
            await task
