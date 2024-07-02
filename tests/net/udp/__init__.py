"""
A module implementing UDP-based protocol tests.
"""

# built-in
from contextlib import ExitStack, suppress
from pathlib import Path
from tempfile import TemporaryDirectory

# third-party
from vcorelib import DEFAULT_ENCODING
from vcorelib.paths.context import tempfile
from vcorelib.platform import is_windows

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.udp.tftp import TftpConnection, tftp_read, tftp_write


async def tftp_test(app: AppInfo) -> int:
    """Perform some initialization tasks."""

    with ExitStack() as stack:
        # Windows.
        stack.enter_context(suppress(PermissionError))
        tmpdir = stack.enter_context(TemporaryDirectory())

        # Set root directory.
        path = Path(tmpdir)
        for conn in app.conn_manager.by_type(TftpConnection):
            conn.set_root(path)

        # Determine 'tftp_server' port, interact via functional interface.
        server = app.single(pattern="server", kind=TftpConnection)

        msg = "Hello, world!"

        for idx in range(3 if not is_windows() else 1):
            filename = f"{idx}.txt"

            # Confirm we can write and then read.
            assert await tftp_write(server.local_address, msg, filename)

            with tempfile() as dst:
                assert await tftp_read(server.local_address, dst, filename)
                with dst.open("r", encoding=DEFAULT_ENCODING) as path_fd:
                    assert path_fd.read() == msg

    return 0
