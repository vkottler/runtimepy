"""
A module containing useful type definitions for JSON messaging.
"""

# built-in
from typing import Awaitable, Callable, TypeVar

# third-party
from vcorelib.dict.codec import JsonCodec

# internal
from runtimepy.message import JsonMessage

#
# async def message_handler(response: JsonMessage, data: JsonMessage) -> None:
#     """A sample message handler."""
#
MessageHandler = Callable[[JsonMessage, JsonMessage], Awaitable[None]]
MessageHandlers = dict[str, MessageHandler]
RESERVED_KEYS = {"keys_ignored", "__id__", "__log_messages__"}

#
# async def message_handler(response: JsonMessage, data: JsonCodec) -> None:
#     """A sample message handler."""
#
T = TypeVar("T", bound=JsonCodec)
TypedHandler = Callable[[JsonMessage, T], Awaitable[None]]

DEFAULT_LOOPBACK = {"a": 1, "b": 2, "c": 3}
DEFAULT_TIMEOUT = 3
