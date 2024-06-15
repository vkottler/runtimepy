"""
A module implementing a dither controller interface structure.
"""

# internal
from runtimepy.net.arbiter.info import RuntimeStruct
from runtimepy.primitives import Bool, Double


class DitherStruct(RuntimeStruct):
    """A simple dither controller struct."""

    input: Double
    output: Double

    connected: Bool

    def init_env(self) -> None:
        """Initialize this instance's runtime environment."""

        self.output = Double()
        self.env.channel("output", self.output)

        self.input = Double()
        self.connected = Bool(value=True)

        def input_callback(_: float, new: float) -> None:
            """Updates the output when the input is connected."""

            if self.connected:
                # Perform transform here.

                self.output.scaled = new

        self.input.register_callback(input_callback)

        self.env.channel("connected", self.connected, commandable=True)
        self.env.channel("input", self.input, commandable=True)

    def poll(self) -> None:
        """
        A method that other runtime entities can call to perform canonical
        updates to this struct's environment.
        """
