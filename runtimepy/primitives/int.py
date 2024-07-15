"""
A module implementing an integer-primitive interface.
"""

# built-in
from typing import Union as _Union

# internal
from runtimepy.primitives.evaluation import (
    EvalResult,
    Operator,
    PrimitiveIsCloseMixin,
    compare_latest,
)
from runtimepy.primitives.scaling import ChannelScaling, invert
from runtimepy.primitives.types.int import Int8 as _Int8
from runtimepy.primitives.types.int import Int16 as _Int16
from runtimepy.primitives.types.int import Int32 as _Int32
from runtimepy.primitives.types.int import Int64 as _Int64
from runtimepy.primitives.types.int import Uint8 as _Uint8
from runtimepy.primitives.types.int import Uint16 as _Uint16
from runtimepy.primitives.types.int import Uint32 as _Uint32
from runtimepy.primitives.types.int import Uint64 as _Uint64


class BaseIntPrimitive(PrimitiveIsCloseMixin[int]):
    """A simple primitive class for integer primitives."""

    def __init__(
        self, value: int = 0, scaling: ChannelScaling = None, **kwargs
    ) -> None:
        """Initialize this integer primitive."""

        super().__init__(value=value, scaling=scaling, **kwargs)

    def increment(self, amount: int = 1, timestamp_ns: int = None) -> int:
        """Increment this primitive by some amount and return the new value."""

        new_val: int = self.raw.value + amount  # type: ignore
        self.set_value(new_val, timestamp_ns=timestamp_ns)
        return new_val

    async def wait_for_value(
        self,
        value: int | float,
        timeout: float,
        operation: Operator = Operator.EQUAL,
    ) -> EvalResult:
        """Wait for this primitive to reach a specified state."""

        return await compare_latest(  # type: ignore
            self,
            invert(
                value,
                scaling=self.scaling,
                should_round=True,
            ),
            timeout,
            operation=operation,
        )


class Int8Primitive(BaseIntPrimitive):
    """A signed 8-bit primitive."""

    kind = _Int8


Int8 = Int8Primitive


class Int16Primitive(BaseIntPrimitive):
    """A signed 16-bit primitive."""

    kind = _Int16


Int16 = Int16Primitive


class Int32Primitive(BaseIntPrimitive):
    """A signed 32-bit primitive."""

    kind = _Int32


Int32 = Int32Primitive


class Int64Primitive(BaseIntPrimitive):
    """A signed 64-bit primitive."""

    kind = _Int64


Int64 = Int64Primitive


class Uint8Primitive(BaseIntPrimitive):
    """An unsigned 8-bit primitive."""

    kind = _Uint8


Uint8 = Uint8Primitive


class Uint16Primitive(BaseIntPrimitive):
    """An unsigned 16-bit primitive."""

    kind = _Uint16


Uint16 = Uint16Primitive


class Uint32Primitive(BaseIntPrimitive):
    """An unsigned 32-bit primitive."""

    kind = _Uint32


Uint32 = Uint32Primitive


class Uint64Primitive(BaseIntPrimitive):
    """An unsigned 64-bit primitive."""

    kind = _Uint64


Uint64 = Uint64Primitive
SignedInt = _Union[Int8, Int16, Int32, Int64]
UnsignedInt = _Union[Uint8, Uint16, Uint32, Uint64]
