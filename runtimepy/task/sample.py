"""
A sample task interface.
"""

# built-in
import asyncio
from logging import DEBUG

# internal
from runtimepy.channel.environment.sample import poll_sample_env, sample_env
from runtimepy.mixins.trig import TrigMixin
from runtimepy.net.arbiter import AppInfo
from runtimepy.net.arbiter.task import ArbiterTask, TaskFactory
from runtimepy.net.stream.json import JsonMessageConnection


class SampleTask(ArbiterTask, TrigMixin):
    """A base TUI application."""

    async def init(self, app: AppInfo) -> None:
        """Initialize this task with application information."""

        await super().init(app)
        sample_env(self.env)
        TrigMixin.__init__(self, self.env)

    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""

        # Use this to implement / test rate-limited logging.
        with self.log_time("dispatch", level=DEBUG):
            poll_sample_env(self.env)

            # Interact with connections.
            await asyncio.gather(
                *(
                    x.loopback()
                    for x in self.app.search(
                        pattern="client", kind=JsonMessageConnection
                    )
                )
            )

            self.dispatch_trig(self.metrics.dispatches.value)

        return True


class Sample(TaskFactory[SampleTask]):
    """A TUI application factory."""

    kind = SampleTask


class SampleAppTask(ArbiterTask):
    """A base TUI application."""

    app: AppInfo

    async def init(self, app: AppInfo) -> None:
        """Initialize this task with application information."""
        self.app = app

    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""

        for name, struct in self.app.structs.items():
            if "struct" in name:
                struct.poll()

        # Send poll message to peer process.
        for peer in self.app.peers.values():
            peer.send_poll()

        return True


class SampleApp(TaskFactory[SampleAppTask]):
    """A TUI application factory."""

    kind = SampleAppTask
