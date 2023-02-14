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

# internal
from runtimepy.net.connection import Connection as _Connection


class ConnectionManager:
    """A class for managing connection processing at runtime."""

    def __init__(self) -> None:
        """Initialize this connection manager."""
        self.queue: _asyncio.Queue[_Connection] = _asyncio.Queue()
        self._running = False

    async def manage(self, stop_sig: _asyncio.Event) -> None:
        """Handle incoming connections until the stop signal is set."""

        assert not self._running
        self._running = True

        stop_sig_task = _asyncio.create_task(stop_sig.wait())
        tasks: _List[_asyncio.Task[None]] = []
        conns: _List[_Connection] = []
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
            conns = [x for x in conns if not x.disabled]

            # If a new connection was made, register a task for processing
            # it.
            if new_conn_task.done():
                new_conn = new_conn_task.result()
                conns.append(new_conn)
                next_tasks.append(
                    _asyncio.create_task(new_conn.process(stop_sig=stop_sig))
                )
                new_conn_task = None

            # If the stop signal was sent, cancel existing connections.
            if stop_sig.is_set():
                # Allow existing tasks to clean up.
                if new_conn_task is not None:
                    new_conn_task.cancel()
                for task in next_tasks:
                    await task

            tasks = next_tasks

        self._running = False
