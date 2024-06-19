"""
A module implementing signal source structs.
"""

# built-in
from typing import Generic

# internal
from runtimepy.control.env import amplitude
from runtimepy.net.arbiter.info import RuntimeStruct
from runtimepy.primitives import Double, T


class PrimitiveSource(RuntimeStruct, Generic[T]):
    """A simple output-source struct."""

    kind: type[T]

    outputs: list[T]
    amplitudes: list[Double]

    length: int

    def init_source(self) -> None:
        """Initialize this value source."""

    def source(self, index: int) -> float | int | bool:
        """Provide the next value."""

        del index

        return 0.0

    def init_env(self) -> None:
        """Initialize this double-source environment."""

        self.outputs = []
        self.amplitudes = []

        # load 'count' from config
        count = 1

        for idx in range(count):
            # Output channel.
            output = self.kind()
            self.outputs.append(output)
            self.env.channel(f"{idx}.output", output)

            # Amplitude channel.
            self.amplitudes.append(
                amplitude(self.env, Double, name=f"{idx}.amplitude")
            )

        self.init_source()
        self.length = len(self.outputs)

    def poll(self) -> None:
        """Update the outputs."""

        for idx in range(self.length):
            self.outputs[idx].value = self.source(idx)  # type: ignore


class DoubleSource(PrimitiveSource[Double]):
    """A simple double output source."""

    kind = Double
