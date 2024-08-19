"""
A module implementing a simple telemetry sample interface.
"""

# internal
from runtimepy.channel.environment.sample import (
    long_name_int_enum,
    sample_bool_enum,
    sample_fields,
    sample_float,
    sample_int_enum,
)
from runtimepy.mixins.async_command import AsyncCommandProcessingMixin
from runtimepy.net.arbiter import AppInfo
from runtimepy.net.arbiter.struct import (
    TimestampedStruct,
    UdpStructTransceiver,
)
from runtimepy.net.arbiter.task import ArbiterTask, TaskFactory
from runtimepy.net.arbiter.udp import UdpConnectionFactory
from runtimepy.primitives import Uint16
from runtimepy.primitives.byte_order import ByteOrder


class SampleTelemetryStruct(TimestampedStruct):
    """A sample telemetry struct."""

    # Demonstrate simple byte-order control.
    byte_order = ByteOrder.LITTLE_ENDIAN

    def init_env(self) -> None:
        """Initialize this sample environment."""

        super().init_env()

        sample_int_enum(self.env)
        sample_bool_enum(self.env)
        long_name_int_enum(self.env)
        sample_float(self.env)
        sample_fields(self.env)


class SampleTelemetryTransceiver(UdpStructTransceiver[SampleTelemetryStruct]):
    """A sample telemetry sending connection."""

    struct_kind = SampleTelemetryStruct

    def handle_update(
        self,
        timestamp_ns: int,
        instance: SampleTelemetryStruct,
        addr: tuple[str, int],
    ) -> None:
        """Handle individual struct updates."""


class SampleTelemetry(UdpConnectionFactory[SampleTelemetryTransceiver]):
    """A sample telemetry sending-and-receiving connection factory."""

    kind = SampleTelemetryTransceiver


class SampleTelemetryTask(ArbiterTask, AsyncCommandProcessingMixin):
    """A sample telemetry task."""

    rx_conn: SampleTelemetryTransceiver
    tx_conn: SampleTelemetryTransceiver

    flush_count: Uint16

    async def init(self, app: AppInfo) -> None:
        """Initialize this task with application information."""

        await super().init(app)
        self._setup_async_commands()

        self.flush_count = Uint16(value=10)
        self.env.channel(
            "flush_count",
            self.flush_count,
            commandable=True,
            description="Maximum number of samples before flushing telemetry.",
            default=self.flush_count.value,
            controls="steps_1_1000",
        )

        kind = SampleTelemetryTransceiver

        # Setup Receive.
        pattern = "rx"
        self.rx_conn = app.single(pattern=pattern, kind=kind)
        assert self.rx_conn.assign_app_rx(pattern, app) is not None

        # Setup transmit.
        pattern = "tx"
        self.tx_conn = app.single(pattern=pattern, kind=kind)
        assert self.tx_conn.assign_app_tx(pattern, app) is not None

    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""

        self.tx_conn.capture()

        if self.metrics.dispatches.value % self.flush_count.value == 0:
            self.tx_conn.capture(sample=False, flush=True)

        return True


class SampleTelemetryPeriodic(TaskFactory[SampleTelemetryTask]):
    """A sample-task application factory."""

    kind = SampleTelemetryTask
