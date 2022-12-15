"""
A module implementing a primitive-type storage entity.
"""

# built-in
from typing import Dict as _Dict
from typing import Type as _Type
from typing import TypeVar as _TypeVar
from typing import Union as _Union

# internal
from runtimepy.primitives.bool import Bool
from runtimepy.primitives.float import Double, Float, Half
from runtimepy.primitives.int import (
    Int8,
    Int16,
    Int32,
    Int64,
    Uint8,
    Uint16,
    Uint32,
    Uint64,
)

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

Primitives: _Dict[str, _Type[AnyPrimitive]] = {
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

Primitivelike = _Union[_Type[AnyPrimitive], str]


def normalize(value: Primitivelike) -> _Type[AnyPrimitive]:
    """Normalize a type of primitive or a string into a type of primitive."""

    if isinstance(value, str):
        value = value.lower()
        assert value in Primitives, f"No primitive '{value}'!"
        value = Primitives[value]
    return value


def create(value: Primitivelike) -> AnyPrimitive:
    """Create an instance of a primitive."""
    return normalize(value)()
