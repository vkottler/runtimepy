"""
A module implementing a manual-stepping interface (e.g. program/human
controlled clock).
"""

# internal
from runtimepy.net.arbiter.info import RuntimeStruct
from runtimepy.primitives import Bool, Uint32


class ToggleStepper(RuntimeStruct):
    """A simple struct that ties a ."""

    step: Bool
    count: Uint32

    to_poll: set[RuntimeStruct]

    def init_env(self) -> None:
        """Initialize this toggle stepper environment."""

        self.step = Bool()

        # load from config, default 1
        count = 1
        self.count = Uint32(value=count)

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

    def poll(self) -> None:
        """Poll all other entities."""

        for item in self.to_poll:
            item.poll()
