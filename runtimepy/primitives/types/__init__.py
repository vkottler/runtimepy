"""
A module exposing primitive types.
"""

# built-in
from typing import Union as _Union

# internal
from runtimepy.primitives.types.bool import Bool, BooleanType
from runtimepy.primitives.types.float import (
    Double,
    DoubleType,
    Float,
    FloatType,
    Half,
    HalfType,
)
from runtimepy.primitives.types.int import (
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

SignedIntegerType = _Union[Int8Type, Int16Type, Int32Type, Int64Type]
UnsignedIntegerType = _Union[Uint8Type, Uint16Type, Uint32Type, Uint64Type]

AnyIntegerType = _Union[SignedIntegerType, UnsignedIntegerType]

AnyPrimitiveType = _Union[
    AnyIntegerType, HalfType, FloatType, DoubleType, BooleanType
]

PrimitiveTypes: dict[str, AnyPrimitiveType] = {
    # Integer types.
    Int8.name: Int8,
    "int8_t": Int8,
    Int16.name: Int16,
    "int16_t": Int16,
    Int32.name: Int32,
    "int32_t": Int32,
    Int64.name: Int64,
    "int64_t": Int64,
    Uint8.name: Uint8,
    "uint8_t": Uint8,
    Uint16.name: Uint16,
    "uint16_t": Uint16,
    Uint32.name: Uint32,
    "uint32_t": Uint32,
    Uint64.name: Uint64,
    "uint64_t": Uint64,
    # Floating-point types.
    Half.name: Half,
    "std::float16_t": Half,
    Float.name: Float,
    "std::float32_t": Float,
    Double.name: Double,
    "std::float64_t": Double,
    # Boolean type.
    Bool.name: Bool,
    "boolean": Bool,
}

PrimitiveTypelike = _Union[str, AnyPrimitiveType]


def normalize(value: PrimitiveTypelike) -> AnyPrimitiveType:
    """Normalize a primitive type or string into a primitive type."""

    if isinstance(value, str):
        assert value in PrimitiveTypes, f"No type '{value}'!"
        value = PrimitiveTypes[value]
    return value
