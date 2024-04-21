"""
A module implementing a runtimepy peer interface.
"""

# built-in
import asyncio
from io import BytesIO
from typing import Optional, Type

# third-party
from vcorelib.io.types import JsonObject
from vcorelib.logging import LoggerMixin

# internal
from runtimepy import METRICS_NAME
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.channel.registry import ChannelEventMap, ParsedEvent
from runtimepy.message import JsonMessage, MessageProcessor
from runtimepy.message.interface import JsonMessageInterface
from runtimepy.metrics.channel import ChannelMetrics
from runtimepy.net.arbiter.struct import RuntimeStruct, SampleStruct


class RuntimepyPeerInterface(JsonMessageInterface, LoggerMixin):
    """A class implementing an interface for messaging peer subprocesses."""

    poll_period_s: float = 0.01

    struct_type: Type[RuntimeStruct] = SampleStruct

    def __init__(self, name: str, config: JsonObject) -> None:
        """Initialize this instance."""

        self.processor = MessageProcessor()

        self.struct = self.struct_type(name, config)
        self._finalize_struct()

        self.peer_env: Optional[ChannelEnvironment] = None
        self._peer_env_event = asyncio.Event()
        self._telemetry: asyncio.Queue[ParsedEvent] = asyncio.Queue()

        # Set these for JsonMessageInterface.
        LoggerMixin.__init__(self, logger=self.struct.logger)
        self.command = self.struct.command
        JsonMessageInterface.__init__(self)

    def poll_telemetry(self) -> ChannelEventMap:
        """Get a map of channel telemetry."""

        events = []
        while not self._telemetry.empty():
            events.append(self._telemetry.get_nowait())
        return ParsedEvent.by_channel(events)

    def _set_peer_env(self, data: JsonMessage) -> bool:
        """Set the peer's environment."""

        result = False
        if self.peer_env is None:
            self.peer_env = ChannelEnvironment.load_json(data)
            self._peer_env_event.set()
            result = True
        return result

    def _register_handlers(self) -> None:
        """Register connection-specific command handlers."""

        super()._register_handlers()

        async def env_handler(outbox: JsonMessage, inbox: JsonMessage) -> None:
            """A simple channel environment sharing handler."""

            # Exchange environments.
            if self._set_peer_env(inbox):
                outbox.update(self.struct.env.export_json())

        self.basic_handler("env", env_handler)

    async def share_environment(self) -> None:
        """Exchange channel environments."""

        result = await self.wait_json({"env": self.struct.env.export_json()})
        self._set_peer_env(result["env"])

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
            count = len(data)
            self.stderr_metrics.increment(count)

            # Parse channel events.
            if self.peer_env is not None:
                with BytesIO(data) as stream:
                    for event in self.peer_env.channels.parse_event_stream(
                        stream
                    ):
                        self._telemetry.put_nowait(event)
            else:
                self.logger.warning("Dropped %d bytes of telemetry.", count)

    async def handle_stdout(self, data: bytes) -> None:
        """Handle messages from stdout."""

        if data:
            self.stdout_metrics.increment(len(data))

            for msg in self.processor.messages(data):
                await self.process_json(msg)
