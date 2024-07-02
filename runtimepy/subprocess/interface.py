"""
A module implementing a runtimepy peer interface.
"""

# built-in
from argparse import Namespace
import asyncio
from io import BytesIO
from json import dumps
import logging
from logging import INFO, getLogger
from typing import Optional

# third-party
from vcorelib.io.types import JsonObject
from vcorelib.math import RateLimiter

# internal
from runtimepy import METRICS_NAME
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.channel.environment.base import FieldOrChannel
from runtimepy.channel.environment.command import register_env
from runtimepy.channel.environment.command.processor import (
    RemoteCommandProcessor,
)
from runtimepy.message import JsonMessage, MessageProcessor
from runtimepy.message.interface import JsonMessageInterface
from runtimepy.metrics.channel import ChannelMetrics
from runtimepy.mixins.async_command import AsyncCommandProcessingMixin
from runtimepy.net.arbiter.info import RuntimeStruct, SampleStruct

HOST_SUFFIX = ".host"
PEER_SUFFIX = ".peer"


class RuntimepyPeerInterface(
    JsonMessageInterface, AsyncCommandProcessingMixin
):
    """A class implementing an interface for messaging peer subprocesses."""

    poll_period_s: float = 0.01

    struct_type: type[RuntimeStruct] = SampleStruct

    def __init__(self, name: str, config: JsonObject) -> None:
        """Initialize this instance."""

        self.processor = MessageProcessor()

        self.basename = name
        self.struct = self.struct_type(self.basename + HOST_SUFFIX, config)

        self.peer: Optional[RemoteCommandProcessor] = None
        self.peer_config: Optional[JsonMessage] = None
        self.peer_config_event = asyncio.Event()
        self._peer_env_event = asyncio.Event()

        # Set these for JsonMessageInterface.
        AsyncCommandProcessingMixin.__init__(self, logger=self.struct.logger)
        self.log_limiter = RateLimiter.from_s(1.0)
        self.command = self.struct.command

        self._setup_async_commands()
        JsonMessageInterface.__init__(self)

        self.struct_pre_finalize()
        self._finalize_struct()

    def struct_pre_finalize(self) -> None:
        """Configure struct before finalization."""

    def handle_log_message(self, message: JsonMessage) -> None:
        """Handle a log message."""

        logger = self.logger
        msg = "remote: " + message["msg"]

        if self.peer is not None:
            logger = self.peer.logger
            msg = message["msg"]

        logger.log(message.get("level", INFO), msg, *message.get("args", []))

    @property
    def peer_name(self) -> str:
        """Get the name of the peer's environment."""
        return self.basename + PEER_SUFFIX

    def _set_peer_env(self, data: JsonMessage) -> bool:
        """Set the peer's environment."""

        result = False

        if self.peer is None:
            self.peer = RemoteCommandProcessor(
                ChannelEnvironment.load_json(data), getLogger(self.peer_name)
            )

            def send_cmd_hook(
                args: Namespace, channel: Optional[FieldOrChannel]
            ) -> None:
                """Command hook for sending JSON commands."""
                self._handle_command(args, channel)

            self.peer.hooks.append(send_cmd_hook)

            self.peer.logger.info("Loaded.")

            # Register both environments.
            register_env(self.struct.name, self.struct.command)
            register_env(self.peer_name, self.peer)

            self._peer_env_event.set()
            result = True

        return result

    async def handle_command(
        self, args: Namespace, channel: Optional[FieldOrChannel]
    ) -> None:
        """Handle a command."""

        if args.remote:
            cli_args = [args.command]
            if args.force:
                cli_args.append("-f")
            cli_args.append(args.channel)

            self.logger.info(
                "Remote command: %s",
                str(
                    await self.channel_command(
                        " ".join(cli_args + args.extra), environment=args.env
                    )
                ),
            )

    def _register_handlers(self) -> None:
        """Register connection-specific command handlers."""

        super()._register_handlers()

        async def env_handler(outbox: JsonMessage, inbox: JsonMessage) -> None:
            """A simple channel environment sharing handler."""

            # Exchange environments.
            if self._set_peer_env(inbox):
                outbox.update(self.struct.env.export_json())

        self.basic_handler("env", env_handler)

        async def config_handler(
            outbox: JsonMessage, inbox: JsonMessage
        ) -> None:
            """Store peer's configuration."""

            if self.peer_config is None:
                self.peer_config = inbox["config"]
                outbox["config"] = self.struct.config
                self.logger.info(
                    "Peer's configuration: '%s'.",
                    dumps(self.peer_config, indent=4),
                )
                self.peer_config_event.set()

        self.basic_handler("config", config_handler)

    async def share_config(self, data: JsonMessage) -> None:
        """Exchange configuration data."""

        await self.wait_json({"config": data})

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
            if self.peer is not None:
                with BytesIO(data) as stream:
                    for event in self.peer.env.parse_event_stream(stream):
                        self.peer.env.ingest(event)
            else:
                self.governed_log(
                    self.log_limiter,
                    "Dropped %d bytes of telemetry.",
                    count,
                    level=logging.WARNING,
                )

    async def handle_stdout(self, data: bytes) -> None:
        """Handle messages from stdout."""

        if data:
            self.stdout_metrics.increment(len(data))

            for msg in self.processor.messages(data):
                await self.process_json(msg)

    async def poll_handler(self) -> None:
        """Handle a 'poll' message."""
        self.struct.poll()
