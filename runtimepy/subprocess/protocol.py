"""
A module implementing a subprocess protocol.
"""

# built-in
from asyncio import (
    Event,
    Queue,
    ReadTransport,
    SubprocessProtocol,
    SubprocessTransport,
    WriteTransport,
)
from subprocess import Popen
from typing import Optional, cast

# third-party
from vcorelib.math import metrics_time_ns


class RuntimepySubprocessProtocol(SubprocessProtocol):
    """A simple subprocess protocol implementation."""

    start_time: int
    elapsed_time: int

    transport: SubprocessTransport
    subproc: Popen[bytes]

    stdin: WriteTransport
    stdout_transport: ReadTransport
    stderr_transport: ReadTransport

    stdout_queue: Optional[Queue[bytes]]
    stderr_queue: Optional[Queue[bytes]]

    exited: Event

    @property
    def stdout(self) -> Queue[bytes]:
        """Get this instance's standard output queue."""
        assert self.stdout_queue is not None
        return self.stdout_queue

    @property
    def stderr(self) -> Queue[bytes]:
        """Get this instance's standard error queue."""
        assert self.stderr_queue is not None
        return self.stderr_queue

    @property
    def pid(self) -> int:
        """Get this subprocess's protocol identifier."""
        return self.transport.get_pid()

    def connection_made(self, transport) -> None:
        """Initialize this protocol."""

        self.start_time = metrics_time_ns()
        self.elapsed_time = -1

        self.stdout_queue = None
        self.stderr_queue = None
        self.exited = Event()

        self.transport = transport
        self.subproc = self.transport.get_extra_info("subprocess")

        transport = self.transport.get_pipe_transport(0)
        self.stdin = cast(WriteTransport, transport)

        transport = self.transport.get_pipe_transport(1)
        self.stdout_transport = cast(ReadTransport, transport)

        transport = self.transport.get_pipe_transport(2)
        self.stderr_transport = cast(ReadTransport, transport)

    def pipe_data_received(self, fd: int, data: bytes) -> None:
        """Handle incoming pipe data."""

        if fd == 1 and self.stdout_queue is not None:
            self.stdout_queue.put_nowait(data)
        elif self.stderr_queue is not None:
            assert fd == 2, fd
            self.stderr_queue.put_nowait(data)

    def pipe_connection_lost(self, fd: int, exc) -> None:
        """Handle a pipe connection closing."""

        if fd == 1:
            self._flush_stdout()
        elif fd == 2:
            self._flush_stderr()

    def _flush_stdout(self) -> None:
        """Flush standard output."""
        if self.stdout_queue is not None:
            self.stdout_queue.put_nowait(bytes())

    def _flush_stderr(self) -> None:
        """Flush standard error."""
        if self.stderr_queue is not None:
            self.stderr_queue.put_nowait(bytes())

    def process_exited(self) -> None:
        """Handle process exit."""

        self.elapsed_time = metrics_time_ns() - self.start_time

        self._flush_stdout()
        self._flush_stderr()

        self.exited.set()
