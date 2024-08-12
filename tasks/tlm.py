"""
A module implementing a simple telemetry sample interface.
"""

# built-in
import asyncio

from runtimepy.channel.environment.sample import (
    long_name_int_enum,
    sample_bool_enum,
    sample_fields,
    sample_float,
    sample_int_enum,
)

# internal
from runtimepy.net.arbiter import AppInfo
from runtimepy.net.arbiter.struct import (
    TimestampedStruct,
    UdpStructTransceiver,
)
from runtimepy.net.arbiter.udp import UdpConnectionFactory


class SampleTelemetryStruct(TimestampedStruct):
    """A sample telemetry struct."""

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


async def sample_app(app: AppInfo) -> int:
    """Test telemetry sending and receiving."""

    # Setup Receive.
    pattern = "rx"
    rx_conn = app.single(pattern=pattern, kind=SampleTelemetryTransceiver)
    assert rx_conn.assign_app_rx(pattern, app) is not None

    # Setup transmit.
    pattern = "tx"
    tx_conn = app.single(pattern=pattern, kind=SampleTelemetryTransceiver)
    assert tx_conn.assign_app_tx(pattern, app) is not None

    # Do some sending and receiving / polling!
    iteration = 0
    forever = app.config_param("forever", False)
    while not app.stop.is_set() and (iteration < 31 or forever):
        tx_conn.capture()
        iteration += 1

        if iteration % 10 == 0:
            tx_conn.capture(sample=False, flush=True)

        await asyncio.sleep(0.01)

    return 0