"""
A module implementing an integer-primitive interface.
"""

# built-in
from typing import Union as _Union

# internal
from runtimepy.primitives.base import Primitive as _Primitive
from runtimepy.primitives.scaling import ChannelScaling
from runtimepy.primitives.types.int import Int8 as _Int8
from runtimepy.primitives.types.int import Int16 as _Int16
from runtimepy.primitives.types.int import Int32 as _Int32
from runtimepy.primitives.types.int import Int64 as _Int64
from runtimepy.primitives.types.int import Uint8 as _Uint8
from runtimepy.primitives.types.int import Uint16 as _Uint16
from runtimepy.primitives.types.int import Uint32 as _Uint32
from runtimepy.primitives.types.int import Uint64 as _Uint64


class Int8Primitive(_Primitive[int]):
    """A simple primitive class for integer primitives."""

    kind = _Int8

    def __init__(
        self, value: int = 0, scaling: ChannelScaling = None, **kwargs
    ) -> None:
        """Initialize this integer primitive."""
        super().__init__(value=value, scaling=scaling, **kwargs)


Int8 = Int8Primitive


class Int16Primitive(_Primitive[int]):
    """A simple primitive class for integer primitives."""

    kind = _Int16

    def __init__(
        self, value: int = 0, scaling: ChannelScaling = None, **kwargs
    ) -> None:
        """Initialize this integer primitive."""
        super().__init__(value=value, scaling=scaling, **kwargs)


Int16 = Int16Primitive


class Int32Primitive(_Primitive[int]):
    """A simple primitive class for integer primitives."""

    kind = _Int32

    def __init__(
        self, value: int = 0, scaling: ChannelScaling = None, **kwargs
    ) -> None:
        """Initialize this integer primitive."""
        super().__init__(value=value, scaling=scaling, **kwargs)


Int32 = Int32Primitive


class Int64Primitive(_Primitive[int]):
    """A simple primitive class for integer primitives."""

    kind = _Int64

    def __init__(
        self, value: int = 0, scaling: ChannelScaling = None, **kwargs
    ) -> None:
        """Initialize this integer primitive."""
        super().__init__(value=value, scaling=scaling, **kwargs)


Int64 = Int64Primitive


class Uint8Primitive(_Primitive[int]):
    """A simple primitive class for integer primitives."""

    kind = _Uint8

    def __init__(
        self, value: int = 0, scaling: ChannelScaling = None, **kwargs
    ) -> None:
        """Initialize this integer primitive."""
        super().__init__(value=value, scaling=scaling, **kwargs)


Uint8 = Uint8Primitive


class Uint16Primitive(_Primitive[int]):
    """A simple primitive class for integer primitives."""

    kind = _Uint16

    def __init__(
        self, value: int = 0, scaling: ChannelScaling = None, **kwargs
    ) -> None:
        """Initialize this integer primitive."""
        super().__init__(value=value, scaling=scaling, **kwargs)


Uint16 = Uint16Primitive


class Uint32Primitive(_Primitive[int]):
    """A simple primitive class for integer primitives."""

    kind = _Uint32

    def __init__(
        self, value: int = 0, scaling: ChannelScaling = None, **kwargs
    ) -> None:
        """Initialize this integer primitive."""
        super().__init__(value=value, scaling=scaling, **kwargs)


Uint32 = Uint32Primitive


class Uint64Primitive(_Primitive[int]):
    """A simple primitive class for integer primitives."""

    kind = _Uint64

    def __init__(
        self, value: int = 0, scaling: ChannelScaling = None, **kwargs
    ) -> None:
        """Initialize this integer primitive."""
        super().__init__(value=value, scaling=scaling, **kwargs)


Uint64 = Uint64Primitive
SignedInt = _Union[Int8, Int16, Int32, Int64]
UnsignedInt = _Union[Uint8, Uint16, Uint32, Uint64]
