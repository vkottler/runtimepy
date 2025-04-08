"""
A module implementing a channel-event protocol.
"""

# built-in
from contextlib import contextmanager
from typing import BinaryIO, Iterator

# third-party
from vcorelib.math import to_nanos

# internal
from runtimepy.channel.event.header import PrimitiveEventHeader
from runtimepy.metrics.channel import ChannelMetrics
from runtimepy.primitives import AnyPrimitive


class PrimitiveEvent:
    """A class implementing a simple channel-even interface."""

    def __init__(
        self,
        primitive: AnyPrimitive,
        identifier: int,
    ) -> None:
        """Initialize this instance."""

        self.primitive = primitive
        self.header = PrimitiveEventHeader.instance()
        PrimitiveEventHeader.init_header(self.header, identifier)
        self.prev_ns: int = 0
        self.min_period_ns: int = 0
        self.streaming = False

    def set_min_period(self, min_period_s: float) -> None:
        """Set a minimum period."""

        assert min_period_s > 0, min_period_s
        self.min_period_ns = to_nanos(min_period_s)

    @contextmanager
    def registered(
        self,
        stream: BinaryIO,
        flush: bool = False,
        channel: ChannelMetrics = None,
        force: bool = False,
    ) -> Iterator[None]:
        """Register a stream as a managed context."""

        assert not self.streaming, "Already streaming!"

        def callback(_, __) -> None:
            """Emit a change event to the stream."""
            self._poll(stream, flush=flush, channel=channel, force=force)

        # Poll immediately.
        self.prev_ns = 0

        self._poll(stream, flush=flush, channel=channel)

        raw = self.primitive
        ident = raw.register_callback(callback)

        self.streaming = True
        yield
        assert raw.remove_callback(ident)
        self.streaming = False

    def _poll(
        self,
        stream: BinaryIO,
        flush: bool = False,
        channel: ChannelMetrics = None,
        force: bool = False,
    ) -> int:
        """
        Poll this event so that if the underlying channel has changed since the
        last write, we write another event.
        """

        written = 0

        # Check timestamp and update header if necessary.
        raw = self.primitive
        curr_ns = raw.last_updated_ns

        if force or curr_ns - self.prev_ns >= self.min_period_ns:
            self.prev_ns = curr_ns
            self.header["timestamp"] = curr_ns

            # Write header then value.
            array = self.header
            written += array.to_stream(stream)
            written += raw.to_stream(stream, byte_order=array.byte_order)
            if flush:
                stream.flush()

        if channel is not None:
            channel.increment(written)

        return written
