"""
A module containing useful type definitions for JSON messaging.
"""

# built-in
from typing import Any, Awaitable, Callable, Dict, TypeVar

# third-party
from vcorelib.dict.codec import JsonCodec

JsonMessage = Dict[str, Any]

#
# async def message_handler(response: JsonMessage, data: JsonMessage) -> None:
#     """A sample message handler."""
#
MessageHandler = Callable[[JsonMessage, JsonMessage], Awaitable[None]]
MessageHandlers = Dict[str, MessageHandler]
RESERVED_KEYS = {"keys_ignored", "__id__", "__log_messages__"}

#
# async def message_handler(response: JsonMessage, data: JsonCodec) -> None:
#     """A sample message handler."""
#
T = TypeVar("T", bound=JsonCodec)
TypedHandler = Callable[[JsonMessage, T], Awaitable[None]]

DEFAULT_LOOPBACK = {"a": 1, "b": 2, "c": 3}
DEFAULT_TIMEOUT = 3
