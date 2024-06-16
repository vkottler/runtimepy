"""
A module implementing a type interface for integers.
"""

# internal
from runtimepy.primitives.types.base import Int8Ctype as _Int8Ctype
from runtimepy.primitives.types.base import Int16Ctype as _Int16Ctype
from runtimepy.primitives.types.base import Int32Ctype as _Int32Ctype
from runtimepy.primitives.types.base import Int64Ctype as _Int64Ctype
from runtimepy.primitives.types.base import PrimitiveType as _PrimitiveType
from runtimepy.primitives.types.base import Uint8Ctype as _Uint8Ctype
from runtimepy.primitives.types.base import Uint16Ctype as _Uint16Ctype
from runtimepy.primitives.types.base import Uint32Ctype as _Uint32Ctype
from runtimepy.primitives.types.base import Uint64Ctype as _Uint64Ctype
from runtimepy.primitives.types.bounds import IntegerBounds


class Int8Type(_PrimitiveType[_Int8Ctype]):
    """A simple type interface for int8's."""

    name = "int8"
    c_type = _Int8Ctype
    python_type = int

    def __init__(self) -> None:
        """Initialize this type."""
        super().__init__("b")
        assert self.is_integer
        self.int_bounds = IntegerBounds.create(1, True)


Int8 = Int8Type()


class Int16Type(_PrimitiveType[_Int16Ctype]):
    """A simple type interface for int16's."""

    name = "int16"
    c_type = _Int16Ctype
    python_type = int

    def __init__(self) -> None:
        """Initialize this type."""
        super().__init__("h")
        assert self.is_integer
        self.int_bounds = IntegerBounds.create(2, True)


Int16 = Int16Type()


class Int32Type(_PrimitiveType[_Int32Ctype]):
    """A simple type interface for int32's."""

    name = "int32"
    c_type = _Int32Ctype
    python_type = int

    def __init__(self) -> None:
        """Initialize this type."""
        super().__init__("i")
        assert self.is_integer
        self.int_bounds = IntegerBounds.create(4, True)


Int32 = Int32Type()


class Int64Type(_PrimitiveType[_Int64Ctype]):
    """A simple type interface for int64's."""

    name = "int64"
    c_type = _Int64Ctype
    python_type = int

    def __init__(self) -> None:
        """Initialize this type."""
        super().__init__("q")
        assert self.is_integer
        self.int_bounds = IntegerBounds.create(8, True)


Int64 = Int64Type()


class Uint8Type(_PrimitiveType[_Uint8Ctype]):
    """A simple type interface for uint8's."""

    name = "uint8"
    c_type = _Uint8Ctype
    python_type = int

    def __init__(self) -> None:
        """Initialize this type."""
        super().__init__("B", signed=False)
        assert self.is_integer
        self.int_bounds = IntegerBounds.create(1, False)


Uint8 = Uint8Type()


class Uint16Type(_PrimitiveType[_Uint16Ctype]):
    """A simple type interface for uint16's."""

    name = "uint16"
    c_type = _Uint16Ctype
    python_type = int

    def __init__(self) -> None:
        """Initialize this type."""
        super().__init__("H", signed=False)
        assert self.is_integer
        self.int_bounds = IntegerBounds.create(2, False)


Uint16 = Uint16Type()


class Uint32Type(_PrimitiveType[_Uint32Ctype]):
    """A simple type interface for uint32's."""

    name = "uint32"
    c_type = _Uint32Ctype
    python_type = int

    def __init__(self) -> None:
        """Initialize this type."""
        super().__init__("I", signed=False)
        assert self.is_integer
        self.int_bounds = IntegerBounds.create(4, False)


Uint32 = Uint32Type()


class Uint64Type(_PrimitiveType[_Uint64Ctype]):
    """A simple type interface for uint64's."""

    name = "uint64"
    c_type = _Uint64Ctype
    python_type = int

    def __init__(self) -> None:
        """Initialize this type."""
        super().__init__("Q", signed=False)
        assert self.is_integer
        self.int_bounds = IntegerBounds.create(8, False)


Uint64 = Uint64Type()
