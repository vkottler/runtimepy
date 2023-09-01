"""
A module implementing a JSON message connection interface.
"""

import asyncio

# built-in
from copy import copy
from json import JSONDecodeError, dumps, loads
from typing import Any, Awaitable, Callable, Dict, Tuple, Type, TypeVar, Union

# third-party
from vcorelib.dict.codec import JsonCodec

# internal
from runtimepy.net.stream.string import StringMessageConnection
from runtimepy.net.udp import UdpConnection

JsonMessage = Dict[str, Any]

#
# def message_handler(response: JsonMessage, data: JsonMessage) -> None:
#     """A sample message handler."""
#
MessageHandler = Callable[[JsonMessage, JsonMessage], Awaitable[None]]
MessageHandlers = Dict[str, MessageHandler]
RESERVED_KEYS = {"keys_ignored", "__id__"}

#
# def message_handler(response: JsonMessage, data: JsonCodec) -> None:
#     """A sample message handler."""
#
T = TypeVar("T", bound=JsonCodec)
TypedHandler = Callable[[JsonMessage, T], Awaitable[None]]

DEFAULT_LOOPBACK = {"a": 1, "b": 2, "c": 3}
DEFAULT_TIMEOUT = 3


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


class JsonMessageConnection(StringMessageConnection):
    """A connection interface for JSON messaging."""

    def _register_handlers(self) -> None:
        """Register connection-specific command handlers."""

    def init(self) -> None:
        """Initialize this instance."""

        super().init()

        self.handlers: MessageHandlers = {}
        self.typed_handlers: Dict[
            str, Tuple[Type[JsonCodec], TypedHandler[Any]]
        ] = {}

        self.curr_id: int = 1

        self.ids_waiting: Dict[int, asyncio.Event] = {}
        self.id_responses: Dict[int, JsonMessage] = {}

        # Standard handlers.
        self.basic_handler("loopback")

        self._register_handlers()

    def _validate_key(self, key: str) -> str:
        """Validate a handler key."""

        assert self._valid_new_key(key), key
        return key

    def _valid_new_key(self, key: str) -> bool:
        """Determine if a key is valid."""

        return (
            key not in self.handlers
            and key not in self.typed_handlers
            and key not in RESERVED_KEYS
        )

    def basic_handler(
        self, key: str, handler: MessageHandler = loopback_handler
    ) -> None:
        """Register a basic handler."""

        self.handlers[self._validate_key(key)] = handler

    def typed_handler(
        self, key: str, kind: Type[T], handler: TypedHandler[T]
    ) -> None:
        """Register a typed handler."""

        self.typed_handlers[self._validate_key(key)] = (kind, handler)

    def send_json(
        self, data: Union[JsonMessage, JsonCodec], addr: Tuple[str, int] = None
    ) -> None:
        """Send a JSON message."""

        if isinstance(data, JsonCodec):
            data = data.asdict()

        self.send_message_str(dumps(data, separators=(",", ":")), addr=addr)

    async def wait_json(
        self,
        data: Union[JsonMessage, JsonCodec],
        addr: Tuple[str, int] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> JsonMessage:
        """Send a JSON message and wait for a response."""

        if isinstance(data, JsonCodec):
            data = data.asdict()

        data = copy(data)
        assert "__id__" not in data, data
        data["__id__"] = self.curr_id

        got_response = asyncio.Event()

        ident = self.curr_id
        self.curr_id += 1

        assert ident not in self.ids_waiting
        self.ids_waiting[ident] = got_response

        # Send message and await response.
        self.send_json(data, addr=addr)

        assert await event_wait(
            got_response, timeout
        ), f"No response received in {timeout} seconds!"

        # Return the result.
        result = self.id_responses[ident]
        del self.id_responses[ident]

        return result

    async def loopback(
        self,
        data: JsonMessage = None,
        addr: Tuple[str, int] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> bool:
        """Perform a simple loopback test on this connection."""

        if data is None:
            data = DEFAULT_LOOPBACK

        message = {"loopback": data}
        response = await self.wait_json(message, addr=addr, timeout=timeout)
        status = response == message

        self.logger.info(
            "Loopback result: '%s' (%s).",
            response,
            "success" if status else "fail",
        )

        return status

    async def async_init(self) -> bool:
        """A runtime initialization routine (executes during 'process')."""

        # Check loopback if it makes sense to.
        result = await super().async_init()

        # Only not-connected UDP connections can't do this.
        if (
            result
            and hasattr("self", "remote_address")
            or not isinstance(self, UdpConnection)
        ):
            result = await self.loopback()

        return result

    async def process_json(
        self, data: JsonMessage, addr: Tuple[str, int] = None
    ) -> bool:
        """Process a JSON message."""

        response: JsonMessage = {}

        keys_ignored = []

        tasks = []

        sub_responses: JsonMessage = {}

        for key, item in data.items():
            if self._valid_new_key(key):
                keys_ignored.append(key)
                continue

            sub_response: JsonMessage = {}

            # Prepare handler. Each sets its own response data.
            if key in self.handlers:
                tasks.append(self.handlers[key](sub_response, item))
            elif key in self.typed_handlers:
                kind, handler = self.typed_handlers[key]
                tasks.append(handler(sub_response, kind.create(item)))

            sub_responses[key] = sub_response

        # Run handlers in parallel.
        if tasks:
            await asyncio.gather(*tasks)

        # Promote sub-responses to message output.
        for key, sub_response in sub_responses.items():
            if sub_response:
                response[key] = sub_response
        del sub_responses

        if keys_ignored:
            response["keys_ignored"] = sorted(keys_ignored)

        # If a message identifier is present, send one in the response.
        if "__id__" in data:
            ident = data["__id__"]
            if ident in self.ids_waiting:
                del data["__id__"]
                self.id_responses[ident] = data
                event = self.ids_waiting[ident]
                del self.ids_waiting[ident]
                event.set()
            response["__id__"] = ident

        if response:
            self.send_json(response, addr=addr)

        return True

    async def process_message(
        self, data: str, addr: Tuple[str, int] = None
    ) -> bool:
        """Process a string message."""

        result = True

        try:
            decoded = loads(data)

            if decoded and isinstance(decoded, dict):
                result = await self.process_json(decoded, addr=addr)
            else:
                self.logger.error("Ignoring message '%s'.", data)
        except JSONDecodeError as exc:
            self.logger.exception("Couldn't decode '%s': %s", data, exc)

        return result
