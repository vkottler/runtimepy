"""
A module defining some useful JSON message handlers.
"""

# built-in
import asyncio

# third-party
from vcorelib.dict import MergeStrategy
from vcorelib.dict.codec import BasicDictCodec
from vcorelib.io import ARBITER
from vcorelib.paths import find_file

# internal
from runtimepy.channel.environment.command.processor import (
    ChannelCommandProcessor,
)
from runtimepy.message import JsonMessage
from runtimepy.message.types import TypedHandler
from runtimepy.schemas import RuntimepyDictCodec


class ChannelCommand(RuntimepyDictCodec, BasicDictCodec):
    """A schema-validated find-file request."""

    data: JsonMessage


def channel_env_handler(
    envs: dict[str, ChannelCommandProcessor], default: ChannelCommandProcessor
) -> TypedHandler[ChannelCommand]:
    """Create a channel-environment map command handler."""

    async def handler(outbox: JsonMessage, request: ChannelCommand) -> None:
        """Handle a JSON command for channel environments."""

        if request.data["is_request"]:
            outbox["is_request"] = False

            env_name = request.data["environment"]

            env = envs.get(env_name)
            if env_name == "default":
                env = default

            # Run the command if we have the environment.
            if env is not None:
                result = env.command(request.data["command"])
                outbox["success"] = result.success
                outbox["reason"] = result.reason

            # Respond with an error (environment not found).
            else:
                outbox["success"] = False
                outbox["reason"] = (
                    f"No environment '{env_name}', options: {envs.keys()}."
                )

    return handler


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


class FindFile(RuntimepyDictCodec, BasicDictCodec):
    """A schema-validated find-file request."""

    data: JsonMessage


async def find_file_request_handler(
    outbox: JsonMessage, request: FindFile
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

        # Attempt to decode the file if requested.
        if request.data["decode"]:
            decoded = {"success": False, "data": {}, "time_ns": -1}

            if path is not None:
                result = ARBITER.decode(
                    path,
                    includes_key=request.data["includes_key"],
                    expect_overwrite=request.data["expect_overwrite"],
                    strategy=(
                        MergeStrategy.UPDATE
                        if request.data["update"]
                        else MergeStrategy.RECURSIVE
                    ),
                )
                decoded["success"] = result.success
                decoded["data"] = result.data
                decoded["time_ns"] = result.time_ns

            outbox["decoded"] = decoded
