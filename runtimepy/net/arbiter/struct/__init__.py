"""
A module implementing runtime struct interfaces.
"""

# built-in
from io import BytesIO
from typing import Generic, Iterator, TypeVar

# third-party
from vcorelib.math import default_time_ns
from vcorelib.math.keeper import TimeSource

# internal
from runtimepy.net.arbiter.info import RuntimeStruct
from runtimepy.net.udp.connection import UdpConnection
from runtimepy.primitives import Uint16, Uint64
from runtimepy.primitives.serializable.framer import SerializableFramer


class TimestampedStruct(RuntimeStruct):
    """A bast struct with a timestamp field."""

    log_level_channel = False

    time_keeper: TimeSource = default_time_ns

    timestamp: Uint64
    sequence: Uint16

    def init_env(self) -> None:
        """Initialize this sample environment."""

        names = list(self.env.names)
        assert len(names) == 0, (
            "Timestamp is assumed to be the first channel!",
            names,
        )

        self.timestamp = Uint64(value=type(self).time_keeper())
        self.env.channel(
            "timestamp",
            self.timestamp,
            description=(
                "The nanosecond timestamp when this struct "
                "instance was last updated."
            ),
        )

        self.sequence = Uint16()
        self.env.channel(
            "sequence",
            self.sequence,
            description="A monotonic counter (per instance update).",
        )

    def update_single(self, data: bytes) -> int:
        """Update this struct instance and return the nanosecond timestamp."""

        # Read timestamp.
        timestamp_ns = self.timestamp.decode(
            data[: self.timestamp.size], byte_order=self.array.byte_order
        )

        # Update all array primitives and return timestamp.
        self.array.update(data, timestamp_ns=timestamp_ns)
        return timestamp_ns

    def process_datagram(self, data: bytes) -> Iterator[int]:
        """Process an array message."""

        size = self.array.size

        # Quick sanity check.
        data_len = len(data)
        assert data_len % size == 0

        with BytesIO(data) as stream:
            for _ in range(data_len // size):
                yield self.update_single(stream.read(size))

    def poll(self) -> None:
        """Update this instance's timestamp."""

        self.timestamp.value = type(self).time_keeper()
        self.sequence.increment()


T = TypeVar("T", bound=TimestampedStruct)


class UdpStructSender(UdpConnection, Generic[T]):
    """A connection that can send arrays of structs."""

    # Need to extend the connection factory interface to set these.
    struct_tx: T

    def init(self) -> None:
        """Initialize this instance."""

        self.framer_tx = SerializableFramer(self.struct_tx.array, self.mtu())

    def capture(self, sample: bool = True, flush: bool = False) -> None:
        """Sample this struct and possibly send telemetry."""

        if sample:
            self.struct_tx.poll()

        result = self.framer_tx.capture(sample=sample, flush=flush)
        if result:
            self.sendto(result)


class UdpStructReceiver(UdpConnection, Generic[T]):
    """A connection that can receive arrays of structs."""

    # Need to extend the connection factory interface to set these.
    struct_rx: T

    def handle_update(self, timestamp_ns: int, addr: tuple[str, int]) -> None:
        """Handle individual struct updates."""

    async def process_datagram(
        self, data: bytes, addr: tuple[str, int]
    ) -> bool:
        """Process an array of struct instances."""

        for timestamp_ns in self.struct_rx.process_datagram(data):
            self.handle_update(timestamp_ns, addr)

        return True
