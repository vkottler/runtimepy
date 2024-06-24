"""
A module implementing a manual-stepping interface (e.g. program/human
controlled clock).
"""

# built-in
from typing import cast

# third-party
from vcorelib.math import (
    RateTracker,
    SimulatedTime,
    default_time_ns,
    from_nanos,
    metrics_time_ns,
    restore_time_source,
    set_simulated_source,
)

# internal
from runtimepy.net.arbiter import AppInfo
from runtimepy.net.arbiter.info import RuntimeStruct
from runtimepy.net.arbiter.task import ArbiterTask, TaskFactory
from runtimepy.net.manager import ConnectionManager
from runtimepy.net.server.websocket import RuntimepyWebsocketConnection
from runtimepy.primitives import Bool, Double, Uint32

DONT_POLL_SET = {
    "ToggleStepper",
    "UiState",
    "SampleStruct",
}


def should_poll(kind: type[RuntimeStruct]) -> bool:
    """
    Determine if a toggle stepper should poll the provided type of struct.
    """
    return kind.__name__ not in DONT_POLL_SET and not kind.__name__.startswith(
        "Rt"
    )


def refresh_all_plots(manager: ConnectionManager) -> None:
    """Signal to clients to refresh all data."""

    for conn in manager.by_type(RuntimepyWebsocketConnection):
        for interface in conn.send_interfaces.values():
            interface({"actions": ["clear_points"]})


class ToggleStepper(RuntimeStruct):
    """A simple struct that ties a clock toggle to various runtime entities."""

    step: Bool
    simulate_time: Bool

    time_s: Double

    count: Uint32
    counts: Uint32
    count_rate: Double
    count_rate_tracker: RateTracker

    to_poll: set[RuntimeStruct]

    timer: SimulatedTime

    def _poll_time(self) -> None:
        """Update current time."""
        self.time_s.value = from_nanos(default_time_ns())

    def init_env(self) -> None:
        """Initialize this toggle stepper environment."""

        self.step = Bool()
        self.simulate_time = Bool()

        self.time_s = Double()
        self.env.channel(
            "time_s",
            self.time_s,
            description="Current time (based on default time source).",
        )
        self._poll_time()

        self.count = Uint32(
            value=cast(int, self.config.get("count", 1)),
            time_source=metrics_time_ns,
        )
        self.counts = Uint32(time_source=metrics_time_ns)

        self.count_rate = Double(time_source=metrics_time_ns)
        self.count_rate_tracker = RateTracker(source=metrics_time_ns)

        self.to_poll = set()

        self.timer = SimulatedTime(cast(int, self.config.get("step_dt_ns", 1)))

        def do_step(_: bool, __: bool) -> None:
            """Poll every step edge."""

            for _ in range(self.count.raw.value):  # type: ignore
                self.poll()

        self.step.register_callback(do_step)

        self.env.channel(
            "step",
            self.step,
            description="Toggle to drive 'count' iterations forward.",
            commandable=True,
        )
        self.env.channel(
            "count",
            self.count,
            controls="steps_1_1000",
            description="The number of iterations to step.",
            commandable=True,
        )
        self.env.channel(
            "counts", self.counts, description="Total number of counts."
        )
        self.env.channel(
            "count_rate",
            self.count_rate,
            description="Counts per second (based on realtime clock).",
        )

        self.env.channel(
            "simulate_time",
            self.simulate_time,
            description=(
                "Whether or not time is controlled by the simulated source."
            ),
            commandable=True,
        )

        def do_simulate_time(_: bool, curr: bool) -> None:
            """Toggle the time source selection."""

            if curr:
                set_simulated_source(self.timer)
            else:
                restore_time_source()

            # Signal to the UI to clear plot data.
            refresh_all_plots(self.app.conn_manager)

            self._poll_time()

        self.simulate_time.register_callback(do_simulate_time)

        # Register other structs if configured to do so.
        if self.config.get("global", True):
            for struct in self.app.structs.values():
                if should_poll(type(struct)):  # type: ignore
                    self.to_poll.add(struct)  # type: ignore

    def poll(self) -> None:
        """Poll all other entities."""

        self._poll_time()

        for item in self.to_poll:
            item.poll()

        # Bug?
        # pylint: disable=no-member
        self.counts.value += 1
        # pylint: enable=no-member
        self.count_rate.value = self.count_rate_tracker()

        self.timer.step()


class ToggleStepperTask(ArbiterTask):
    """A task for automatically stepping a toggle-stepper clock."""

    steppers: list[ToggleStepper]

    async def init(self, app: AppInfo) -> None:
        """Initialize this task with application information."""

        await super().init(app)
        self.steppers = list(app.search_structs(ToggleStepper))

        # Start paused.
        self.paused.value = True

    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""

        for stepper in self.steppers:
            stepper.step.toggle()

        return True


class StepperToggler(TaskFactory[ToggleStepperTask]):
    """A task factory for toggle stepper tasks."""

    kind = ToggleStepperTask
