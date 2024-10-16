"""
A module implementing channel-environment telemetry registration.
"""

# built-in
from contextlib import ExitStack, contextmanager
from typing import BinaryIO, Iterator, Optional, cast

# third-party
from vcorelib.names import name_search

# internal
from runtimepy.channel.environment.base import (
    BaseChannelEnvironment as _BaseChannelEnvironment,
)
from runtimepy.channel.event import PrimitiveEvent
from runtimepy.channel.registry import ParsedEvent
from runtimepy.mapping import DEFAULT_PATTERN
from runtimepy.metrics.channel import ChannelMetrics


class TelemetryChannelEnvironment(_BaseChannelEnvironment):
    """A class integrating telemetry streaming."""

    events: list[str]

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

        names: list[str] = []
        events: list[PrimitiveEvent] = []

        # Gather event telemetry emitters for bit-fields.
        for fields in self.fields.fields:
            for name in name_search(fields.fields, pattern, exact=exact):
                names.append(name)
                field = fields.fields[name]

                ident = self.channels.names.identifier(name)
                assert ident is not None, name

                events.append(PrimitiveEvent(field.raw, ident))

        with ExitStack() as stack:
            # Register bit-field event telemetry.
            for event in events:
                stack.enter_context(
                    event.registered(
                        stream, flush=flush, channel=channel, force=True
                    )
                )

            # Register channel telemetry.
            names += stack.enter_context(
                self.channels.registered(
                    stream,
                    pattern=pattern,
                    exact=exact,
                    flush=flush,
                    channel=channel,
                )
            )

            yield names

    def ingest(self, point: ParsedEvent) -> None:
        """
        Update internal state based on an event. Note that the event timestamp
        is not respected.
        """

        if self.fields.has_field(point.name):
            self.fields[point.name].raw.value = point.value  # type: ignore
        else:
            self.set(point.name, point.value)

    def _parse_channel_event(self, name: str) -> Optional[ParsedEvent]:
        """Attempt to parse a channel event from the fifo."""

        result = None
        channels = self.channels

        kind = channels[name].type
        data = channels.event_fifo.pop(kind.size)
        if data is not None:
            result = ParsedEvent(
                name,
                cast(int, channels.event_header["timestamp"]),
                kind.decode(
                    data,
                    byte_order=channels.event_header.array.byte_order,
                ),
            )

        return result

    def _parse_field_event(self, name: str) -> Optional[ParsedEvent]:
        """Attempt to parse a bit-field event from the fifo."""

        result = None

        field = self.fields[name]

        kind = field.raw.kind
        data = self.channels.event_fifo.pop(kind.size)
        if data is not None:
            result = ParsedEvent(
                name,
                cast(int, self.channels.event_header["timestamp"]),
                kind.decode(
                    data,
                    byte_order=self.channels.event_header.array.byte_order,
                ),
            )

        return result

    def parse_event_stream(self, stream: BinaryIO) -> Iterator[ParsedEvent]:
        """Parse individual events from a stream."""

        channels = self.channels

        # Ingest stream.
        channels.event_fifo.ingest(stream.read())

        ident = -1
        name = ""

        keep_going = True
        while keep_going:
            keep_going = False

            # Read header.
            if not channels.header_ready:
                read_size = channels.event_header.size
                data = channels.event_fifo.pop(read_size)
                if data is not None:
                    channels.event_header.array.update(data)

                    # Update local variables.
                    ident = cast(int, channels.event_header["identifier"])
                    name = channels.names.name(ident)  # type: ignore
                    assert name is not None, ident

                    # Update state.
                    channels.header_ready = True
                    keep_going = True
            else:
                event = None

                # Handle bit-field.
                if self.fields.has_field(name):
                    event = self._parse_field_event(name)

                # Handle channel.
                elif name in channels.items:
                    event = self._parse_channel_event(name)

                if event is not None:
                    yield event

                    # Update state.
                    channels.header_ready = False
                    keep_going = True
