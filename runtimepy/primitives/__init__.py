"""
A module implementing a primitive-type storage entity.
"""

# built-in
from typing import TypeVar as _TypeVar
from typing import Union as _Union

# third-party
from vcorelib.python import StrToBool

# internal
from runtimepy.primitives.base import Primitive
from runtimepy.primitives.bool import Bool
from runtimepy.primitives.float import BaseFloatPrimitive, Double, Float, Half
from runtimepy.primitives.int import (
    BaseIntPrimitive,
    Int8,
    Int16,
    Int32,
    Int64,
    SignedInt,
    Uint8,
    Uint16,
    Uint32,
    Uint64,
    UnsignedInt,
)
from runtimepy.primitives.scaling import ChannelScaling, Numeric

__all__ = [
    "ChannelScaling",
    "Numeric",
    "Bool",
    "Double",
    "Float",
    "Half",
    "Int8",
    "Int16",
    "Int32",
    "Int64",
    "Uint8",
    "Uint16",
    "Uint32",
    "Uint64",
    "AnyPrimitive",
    "T",
    "Primitivelike",
    "normalize",
    "create",
    "SignedInt",
    "UnsignedInt",
    "Primitive",
    "StrToBool",
    "BaseIntPrimitive",
    "BaseFloatPrimitive",
]

AnyPrimitive = _Union[
    Int8,
    Int16,
    Int32,
    Int64,
    Uint8,
    Uint16,
    Uint32,
    Uint64,
    Half,
    Float,
    Double,
    Bool,
]

# A type variable for class definitions.
T = _TypeVar(
    "T",
    Int8,
    Int16,
    Int32,
    Int64,
    Uint8,
    Uint16,
    Uint32,
    Uint64,
    Half,
    Float,
    Double,
    Bool,
)

Primitives: dict[str, type[AnyPrimitive]] = {
    Int8().kind.name: Int8,
    Int16().kind.name: Int16,
    Int32().kind.name: Int32,
    Int64().kind.name: Int64,
    Uint8().kind.name: Uint8,
    Uint16().kind.name: Uint16,
    Uint32().kind.name: Uint32,
    Uint64().kind.name: Uint64,
    Half().kind.name: Half,
    Float().kind.name: Float,
    Double().kind.name: Double,
    Bool().kind.name: Bool,
}

Primitivelike = _Union[type[AnyPrimitive], str]


def normalize(value: Primitivelike) -> type[AnyPrimitive]:
    """Normalize a type of primitive or a string into a type of primitive."""

    if isinstance(value, str):
        value = value.lower()
        assert value in Primitives, f"No primitive '{value}'!"
        value = Primitives[value]
    return value


def create(value: Primitivelike, **kwargs) -> AnyPrimitive:
    """Create an instance of a primitive."""
    return normalize(value)(**kwargs)


def normalize_instance(
    value: Primitivelike | AnyPrimitive, **kwargs
) -> AnyPrimitive:
    """Creates a new instance only if necessary."""

    if not isinstance(value, Primitive):
        value = create(value, **kwargs)
    return value
