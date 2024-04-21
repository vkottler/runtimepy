"""
A module implementing a runtimepy peer interface.
"""

# third-party
from vcorelib.logging import LoggerMixin

# internal
from runtimepy import METRICS_NAME
from runtimepy.message import MessageProcessor
from runtimepy.message.interface import JsonMessageInterface
from runtimepy.metrics.channel import ChannelMetrics
from runtimepy.net.arbiter.struct import RuntimeStruct


class RuntimepyPeerInterface(JsonMessageInterface, LoggerMixin):
    """A class implementing an interface for messaging peer subprocesses."""

    poll_period_s: float = 0.01

    def __init__(self, struct: RuntimeStruct) -> None:
        """Initialize this instance."""

        self.processor = MessageProcessor()

        self.struct = struct
        self._finalize_struct()

        # Set these for JsonMessageInterface.
        LoggerMixin.__init__(self, logger=self.struct.logger)
        self.command = self.struct.command
        JsonMessageInterface.__init__(self)

    def _finalize_struct(self) -> None:
        """Initialize struct members."""

        with self.struct.env.names_pushed(METRICS_NAME):
            # stderr channel metrics.
            self.stderr_metrics = ChannelMetrics()
            self.struct.register_channel_metrics(
                "stderr", self.stderr_metrics, "transmitted"
            )

            # stdout channel metrics.
            self.stdout_metrics = ChannelMetrics()
            self.struct.register_channel_metrics(
                "stdout", self.stdout_metrics, "transmitted"
            )

            # stdin channel metrics.
            self.stdin_metrics = ChannelMetrics()
            self.struct.register_channel_metrics(
                "stdin", self.stdin_metrics, "transmitted"
            )

        self.struct.init_env()
        self.struct.env.finalize()

    def poll_metrics(self, time_ns: int = None) -> None:
        """Poll channels."""

        self.stderr_metrics.poll(time_ns=time_ns)
        self.stdout_metrics.poll(time_ns=time_ns)
        self.stdin_metrics.poll(time_ns=time_ns)

    def handle_stderr(self, data: bytes) -> None:
        """Forward stderr."""

        if data:
            self.stderr_metrics.increment(len(data))

            # Parse channel events.
            del data

    async def handle_stdout(self, data: bytes) -> None:
        """Handle messages from stdout."""

        if data:
            self.stdout_metrics.increment(len(data))

            for msg in self.processor.messages(data):
                await self.process_json(msg)
