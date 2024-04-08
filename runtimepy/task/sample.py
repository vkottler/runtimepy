"""
A sample task interface.
"""

# built-in
import asyncio
from logging import DEBUG

# internal
from runtimepy.channel.environment.sample import poll_sample_env, sample_env
from runtimepy.net.arbiter import AppInfo
from runtimepy.net.arbiter.task import ArbiterTask, TaskFactory
from runtimepy.net.stream.json import JsonMessageConnection


class SampleTask(ArbiterTask):
    """A base TUI application."""

    async def init(self, app: AppInfo) -> None:
        """Initialize this task with application information."""

        await super().init(app)
        sample_env(self.env)

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

        return True


class Sample(TaskFactory[SampleTask]):
    """A TUI application factory."""

    kind = SampleTask
