"""
A module implementing runtime struct interfaces.
"""

# built-in
from io import BytesIO
from typing import Generic, Iterator, Optional, TypeVar

# third-party
from vcorelib.math import default_time_ns
from vcorelib.math.keeper import TimeSource

# internal
from runtimepy.net.arbiter.info import AppInfo, RuntimeStruct
from runtimepy.net.mtu import UDP_DEFAULT_MTU, UDP_HEADER_SIZE
from runtimepy.net.udp.connection import UdpConnection
from runtimepy.primitives import Uint16, Uint64
from runtimepy.primitives.serializable.framer import SerializableFramer


class TimestampedStruct(RuntimeStruct):
    """A bast struct with a timestamp field."""

    log_level_channel = False

    time_keeper: TimeSource = default_time_ns

    # Header.
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
        assert data_len % size == 0, (data_len, size)

        with BytesIO(data) as stream:
            for _ in range(data_len // size):
                yield self.update_single(stream.read(size))

    def poll(self) -> None:
        """Update this instance's timestamp."""

        self.timestamp.value = type(self).time_keeper()
        self.sequence.increment()


T = TypeVar("T", bound=TimestampedStruct)


class UdpStructTransceiver(UdpConnection, Generic[T]):
    """A connection that can send and receive arrays of structs."""

    # Sub-class should set this.
    struct_kind: type[T]

    # A factory implementation must call 'assign_tx' below.
    struct_tx: Optional[T] = None
    framer_tx: SerializableFramer

    # Make these private + add 'assign' method?
    struct_rx: Optional[T] = None

    def assign_tx(self, instance: T) -> None:
        """Assign a struct to this connection."""

        assert isinstance(instance, self.struct_kind), (
            instance,
            self.struct_kind,
        )
        assert self.struct_tx is None, "Transmit struct already assigned!"

        self.struct_tx = instance
        self.framer_tx = SerializableFramer(
            self.struct_tx.array, UDP_DEFAULT_MTU
        )

        def get_payload(probe_size: int) -> bytes:
            """Get a data payload suitable for MTU probing."""

            self.framer_tx.set_mtu(probe_size)
            result = None
            while result is None:
                result = self.framer_tx.capture()
            return result

        # This actually sends data over this connection.
        self.framer_tx.set_mtu(
            self.mtu(probe_create=get_payload),
            logger=self.logger,
            protocol_overhead=UDP_HEADER_SIZE,
        )

    def assign_app_tx(self, pattern: str, app: AppInfo) -> Optional[T]:
        """Attempt to assign a transmit struct to this instance."""

        result = None

        candidate = list(
            app.search_structs(pattern=pattern, kind=self.struct_kind)
        )
        if len(candidate) == 1:
            result = candidate[0]
            self.assign_tx(result)

        return result

    def assign_rx(self, instance: T) -> None:
        """Assign a receive struct."""

        assert isinstance(instance, self.struct_kind), (
            instance,
            self.struct_kind,
        )
        assert self.struct_rx is None, "Receive struct already assigned!"

        self.struct_rx = instance

    def assign_app_rx(self, pattern: str, app: AppInfo) -> Optional[T]:
        """Attempt to assign a receive struct to this instance."""

        result = None

        candidate = list(
            app.search_structs(pattern=pattern, kind=self.struct_kind)
        )
        if len(candidate) == 1:
            result = candidate[0]
            self.assign_rx(result)

        return result

    def capture(self, sample: bool = True, flush: bool = False) -> None:
        """Sample this struct and possibly send telemetry."""

        # Should we handle the other branch?
        if self.struct_tx is not None:
            if sample:
                self.struct_tx.poll()

            result = self.framer_tx.capture(sample=sample, flush=flush)
            if result:
                self.sendto(result)

    def handle_update(
        self, timestamp_ns: int, instance: T, addr: tuple[str, int]
    ) -> None:
        """Handle individual struct updates."""

    async def process_datagram(
        self, data: bytes, addr: tuple[str, int]
    ) -> bool:
        """Process an array of struct instances."""

        # Should we handle the other branch?
        if self.struct_rx is not None:
            for timestamp_ns in self.struct_rx.process_datagram(data):
                self.handle_update(timestamp_ns, self.struct_rx, addr)

        return True
