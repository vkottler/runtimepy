"""
A module implementing signal source structs.
"""

# built-in
from abc import abstractmethod
from typing import Any, Generic, cast

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

    @abstractmethod
    def source(self, index: int) -> float | int | bool:
        """Provide the next value."""

    def init_env(self) -> None:
        """Initialize this double-source environment."""

        self.outputs = []
        self.amplitudes = []

        # Load 'count' from config.
        count: int = self.config.get("count", 1)  # type: ignore

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
            # Difficult to avoid cast.
            self.outputs[idx].value = cast(
                Any, self.amplitudes[idx].value * self.source(idx)
            )


class DoubleSource(PrimitiveSource[Double]):
    """A simple double output source."""

    kind = Double
