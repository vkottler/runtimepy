"""
A module defining some useful JSON message handlers.
"""

# built-in
import asyncio

# third-party
from vcorelib.dict.codec import BasicDictCodec
from vcorelib.paths import find_file

# internal
from runtimepy.net.stream.json.types import JsonMessage
from runtimepy.schemas import RuntimepyDictCodec


async def loopback_handler(outbox: JsonMessage, inbox: JsonMessage) -> None:
    """A simple loopback handler."""

    outbox.update(inbox)


async def event_wait(event: asyncio.Event, timeout: float) -> bool:
    """Wait for an event to be set within a timeout."""

    result = True

    try:
        await asyncio.wait_for(event.wait(), timeout)
    except asyncio.TimeoutError:
        result = False

    return result


class FindFileRequest(RuntimepyDictCodec, BasicDictCodec):
    """A schema-validated find-file request."""

    data: JsonMessage


async def find_file_request_handler(
    outbox: JsonMessage, request: FindFileRequest
) -> None:
    """Attempt to find a file path based on the request."""

    if request.data["is_request"]:
        path = find_file(
            request.data["path"],
            *request.data.get("parts", []),
            search_paths=request.data.get("search_paths"),
            include_cwd=request.data["include_cwd"],
            relative_to=request.data.get("relative_to"),
            package=request.data.get("package"),
            package_subdir=request.data["package_subdir"],
        )
        outbox["path"] = str(path) if path is not None else None
        outbox["is_request"] = False
