"""
A module implementing a channel registry.
"""

# built-in
from contextlib import ExitStack, contextmanager
from typing import Any as _Any
from typing import BinaryIO, Iterable, Iterator, NamedTuple
from typing import Optional as _Optional
from typing import Union

# third-party
from vcorelib.io import ByteFifo
from vcorelib.io.types import JsonObject as _JsonObject

# internal
from runtimepy.channel import AnyChannel as _AnyChannel
from runtimepy.channel import Channel as _Channel
from runtimepy.channel import Default as _Default
from runtimepy.channel.event.header import PrimitiveEventHeader
from runtimepy.codec.protocol import Protocol
from runtimepy.mapping import DEFAULT_PATTERN
from runtimepy.metrics.channel import ChannelMetrics
from runtimepy.mixins.regex import CHANNEL_PATTERN as _CHANNEL_PATTERN
from runtimepy.primitives import ChannelScaling, Primitive
from runtimepy.primitives import Primitivelike as _Primitivelike
from runtimepy.primitives import normalize
from runtimepy.primitives.types.base import PythonPrimitive
from runtimepy.registry import Registry as _Registry
from runtimepy.registry.name import NameRegistry as _NameRegistry
from runtimepy.registry.name import RegistryKey as _RegistryKey
from runtimepy.ui.controls import Controlslike, normalize_controls


class ChannelNameRegistry(_NameRegistry):
    """A name registry with a name-matching pattern for channel names."""

    name_regex = _CHANNEL_PATTERN


ChannelEventMap = dict[str, list["ParsedEvent"]]


class ParsedEvent(NamedTuple):
    """A raw channel event."""

    name: str
    timestamp: int
    value: PythonPrimitive

    @staticmethod
    def by_channel(
        event_stream: Iterable["ParsedEvent"],
    ) -> ChannelEventMap:
        """
        Get a dictionary of channel events broken down by individual channels.
        """

        result: ChannelEventMap = {}
        for event in event_stream:
            result.setdefault(event.name, []).append(event)
        return result


class ChannelRegistry(_Registry[_Channel[_Any]]):
    """A runtime enumeration registry."""

    name_registry = ChannelNameRegistry

    event_header: Protocol
    event_fifo: ByteFifo
    header_ready: bool

    @property
    def kind(self) -> type[_Channel[_Any]]:
        """Determine what kind of registry this is."""
        return _Channel

    def init(self, data: _JsonObject) -> None:
        """Perform implementation-specific initialization."""

        super().init(data)
        self.event_header = PrimitiveEventHeader.instance()
        self.header_ready = False
        self.event_fifo = ByteFifo()

    def channel(
        self,
        name: str,
        kind: Union[Primitive[_Any], _Primitivelike],
        commandable: bool = False,
        enum: _RegistryKey = None,
        scaling: ChannelScaling = None,
        description: str = None,
        default: _Default = None,
        controls: Controlslike = None,
        **kwargs,
    ) -> _Optional[_AnyChannel]:
        """Create a new channel."""

        if isinstance(kind, str):
            kind = normalize(kind)

        if isinstance(kind, Primitive):
            primitive = kind
        else:
            primitive = kind()

        if scaling:
            assert not primitive.scaling or scaling == primitive.scaling, (
                scaling,
                primitive.scaling,
            )
            primitive.scaling = scaling

        data: _JsonObject = {
            "type": str(primitive.kind),
            "commandable": commandable,
            **kwargs,
        }
        if enum is not None:
            data["enum"] = enum

        if description:
            data["description"] = description

        if default is not None:
            data["default"] = default

        if controls:
            data["controls"] = normalize_controls(controls)  # type: ignore

        result = self.register_dict(name, data)

        # Replace the underlying primitive, in case it was direclty passed in.
        if result is not None:
            result.update_primitive(primitive)

        return result

    @contextmanager
    def registered(
        self,
        stream: BinaryIO,
        pattern: str = DEFAULT_PATTERN,
        exact: bool = False,
        flush: bool = False,
        channel: ChannelMetrics = None,
    ) -> Iterator[list[str]]:
        """
        Register a stream as a managed context. Returns a list of all channels
        registered.
        """

        with ExitStack() as stack:
            names = []
            for name, chan in self.search(pattern, exact=exact):
                stack.enter_context(
                    chan.event.registered(stream, flush=flush, channel=channel)
                )
                names.append(name)

            yield names
