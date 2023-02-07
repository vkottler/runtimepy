"""
A module implementing a connection manager.
"""

from __future__ import annotations

# built-in
import asyncio as _asyncio
from typing import List as _List
from typing import Optional as _Optional
from typing import TypeVar as _TypeVar

# internal
from runtimepy.net.connection import Connection as _Connection

T = _TypeVar("T", bound=_Connection)


async def manage_connections(
    new_conn_queue: _asyncio.Queue[T], stop_sig: _asyncio.Event
) -> None:
    """Handle incoming connections until the stop signal is set."""

    stop_sig_task = _asyncio.create_task(stop_sig.wait())
    tasks: _List[_asyncio.Task[None]] = []
    conns: _List[T] = []
    new_conn_task: _Optional[_asyncio.Task[T]] = None

    while not stop_sig.is_set():
        # Create a new-connection handler.
        if new_conn_task is None:
            # Wait for a connection to be established.
            new_conn_task = _asyncio.create_task(new_conn_queue.get())

        # Wait for any task to complete.
        await _asyncio.wait(
            [stop_sig_task, new_conn_task] + tasks,  # type: ignore
            return_when=_asyncio.FIRST_COMPLETED,
        )

        # Filter completed tasks out of the working set.
        next_tasks = [x for x in tasks if not x.done()]

        # Filter out disabled connections.
        conns = [x for x in conns if not x.disabled]

        # If a new connection was made, register a task for processing
        # it.
        if new_conn_task.done():
            new_conn = new_conn_task.result()
            conns.append(new_conn)
            next_tasks.append(_asyncio.create_task(new_conn.process()))
            new_conn_task = None

        # If the stop signal was sent, cancel existing connections.
        if stop_sig.is_set():
            for conn in conns:
                conn.disable("application stop")

            # Allow existing tasks to clean up.
            if new_conn_task is not None:
                new_conn_task.cancel()
            for task in next_tasks:
                await task

        tasks = next_tasks
