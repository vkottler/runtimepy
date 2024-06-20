"""
A module implementing a manual-stepping interface (e.g. program/human
controlled clock).
"""

# third-party
from vcorelib.math import (
    SimulatedTime,
    metrics_time_ns,
    restore_time_source,
    set_simulated_source,
)

# internal
from runtimepy.net.arbiter.info import RuntimeStruct
from runtimepy.primitives import Bool, Uint32


class ToggleStepper(RuntimeStruct):
    """A simple struct that ties a ."""

    step: Bool
    simulate_time: Bool

    count: Uint32
    counts: Uint32

    to_poll: set[RuntimeStruct]

    timer: SimulatedTime

    def init_env(self) -> None:
        """Initialize this toggle stepper environment."""

        self.step = Bool()
        self.simulate_time = Bool()

        # load from config, default 1
        count = 1
        self.count = Uint32(value=count, time_source=metrics_time_ns)
        self.counts = Uint32(time_source=metrics_time_ns)

        self.to_poll = set()

        step_dt_ns: int = self.config.get("step_dt_ns", 1)  # type: ignore
        self.timer = SimulatedTime(step_dt_ns)

        def do_step(_: bool, __: bool) -> None:
            """Poll every step edge."""

            for _ in range(self.count.raw.value):  # type: ignore
                self.poll()

                # Bug?
                # pylint: disable=no-member
                self.counts.value += 1
                # pylint: enable=no-member

                self.timer.step()

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

        self.simulate_time.register_callback(do_simulate_time)

        # Register other structs if configured to do so.
        if self.config.get("global", True):
            for struct in self.app.structs.values():
                if not isinstance(struct, ToggleStepper):
                    self.to_poll.add(struct)  # type: ignore

    def poll(self) -> None:
        """Poll all other entities."""

        for item in self.to_poll:
            item.poll()
