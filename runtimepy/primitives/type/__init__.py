"""
A module exposing primitive types.
"""

# built-in
from typing import Dict as _Dict
from typing import Union as _Union

# internal
from runtimepy.primitives.type.bool import Bool, BooleanType
from runtimepy.primitives.type.float import (
    Double,
    DoubleType,
    Float,
    FloatType,
    Half,
    HalfType,
)
from runtimepy.primitives.type.int import (
    Int8,
    Int8Type,
    Int16,
    Int16Type,
    Int32,
    Int32Type,
    Int64,
    Int64Type,
    Uint8,
    Uint8Type,
    Uint16,
    Uint16Type,
    Uint32,
    Uint32Type,
    Uint64,
    Uint64Type,
)

AnyPrimitive = _Union[
    Int8Type,
    Int16Type,
    Int32Type,
    Int64Type,
    Uint8Type,
    Uint16Type,
    Uint32Type,
    Uint64Type,
    HalfType,
    FloatType,
    DoubleType,
    BooleanType,
]

PrimitiveTypes: _Dict[str, AnyPrimitive] = {
    # Integer types.
    Int8.name: Int8,
    Int16.name: Int16,
    Int32.name: Int32,
    Int64.name: Int64,
    Uint8.name: Uint8,
    Uint16.name: Uint16,
    Uint32.name: Uint32,
    Uint64.name: Uint64,
    # Floating-point types.
    Half.name: Half,
    Float.name: Float,
    Double.name: Double,
    # Boolean type.
    Bool.name: Bool,
}

PrimitiveTypelike = _Union[str, AnyPrimitive]


def normalize(value: PrimitiveTypelike) -> AnyPrimitive:
    """Normalize a primitive type or string into a primitive type."""

    if isinstance(value, str):
        assert value in PrimitiveTypes, f"No type '{value}'!"
        value = PrimitiveTypes[value]
    return value
