"""
A module implementing a connection manager.
"""

from __future__ import annotations

# built-in
import asyncio as _asyncio
from typing import List as _List
from typing import Optional as _Optional

# third-party
from vcorelib.asyncio import log_exceptions as _log_exceptions
from vcorelib.math import default_time_ns as _default_time_ns

# internal
from runtimepy.net.connection import Connection as _Connection


class ConnectionManager:
    """A class for managing connection processing at runtime."""

    def __init__(self) -> None:
        """Initialize this connection manager."""
        self.queue: _asyncio.Queue[_Connection] = _asyncio.Queue()
        self._running = False
        self._conns: _List[_Connection] = []

    @property
    def num_connections(self) -> int:
        """Return the number of managed connections."""
        return len(self._conns)

    def reset_metrics(self) -> None:
        """Reset connection metrics."""
        for conn in self._conns:
            conn.metrics.reset()

    def poll_metrics(self, time_ns: int = None) -> None:
        """Poll connection metrics."""

        if time_ns is None:
            time_ns = _default_time_ns()

        for conn in self._conns:
            conn.metrics.poll(time_ns=time_ns)

    async def manage(self, stop_sig: _asyncio.Event) -> None:
        """Handle incoming connections until the stop signal is set."""

        # Allow this method to be reentrant.
        if self._running:
            await stop_sig.wait()
            return

        self._running = True

        stop_sig_task = _asyncio.create_task(stop_sig.wait())
        tasks: _List[_asyncio.Task[None]] = []
        self._conns = []
        new_conn_task: _Optional[_asyncio.Task[_Connection]] = None

        while not stop_sig.is_set():
            # Create a new-connection handler.
            if new_conn_task is None:
                # Wait for a connection to be established.
                new_conn_task = _asyncio.create_task(self.queue.get())

            # Wait for any task to complete.
            await _asyncio.wait(
                [stop_sig_task, new_conn_task] + tasks,  # type: ignore
                return_when=_asyncio.FIRST_COMPLETED,
            )

            # Filter completed tasks out of the working set.
            next_tasks = _log_exceptions(tasks)

            # Filter out disabled connections.
            enabled = []
            for conn in self._conns:
                if not conn.disabled:
                    enabled.append(conn)

                # Check if this connection should be restarted.
                elif conn.auto_restart:
                    next_tasks.append(
                        _asyncio.create_task(conn.process(stop_sig=stop_sig))
                    )
                    enabled.append(conn)

            self._conns = enabled

            # If a new connection was made, register a task for processing
            # it.
            if new_conn_task.done():
                new_conn = new_conn_task.result()
                self._conns.append(new_conn)
                next_tasks.append(
                    _asyncio.create_task(new_conn.process(stop_sig=stop_sig))
                )
                new_conn_task = None

            tasks = next_tasks

        # Allow existing tasks to clean up.
        if new_conn_task is not None:
            new_conn_task.cancel()
        for task in tasks:
            await task

        self._running = False
