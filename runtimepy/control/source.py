"""
A module implementing signal source structs.
"""

# internal
from runtimepy.net.arbiter.info import RuntimeStruct
from runtimepy.primitives import Double


class DoubleSource(RuntimeStruct):
    """A simple output-source struct."""

    output: Double

    def source(self) -> float:
        """Provide the next value."""
        return 0.0

    def init_env(self) -> None:
        """Initialize this double-source environment."""

        self.output = Double()
        self.env.channel("output", self.output)

    def poll(self) -> None:
        """Update the output."""

        # scale by an amplitude channel (should have slider?)
        self.output.value = self.source()
