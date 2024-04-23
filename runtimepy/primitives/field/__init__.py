"""
A module implementing bit flags and fields.
"""

# built-in
from typing import cast as _cast

# third-party
from vcorelib.io.types import JsonObject as _JsonObject

# internal
from runtimepy.mixins.enum import EnumMixin as _EnumMixin
from runtimepy.mixins.regex import CHANNEL_PATTERN as _CHANNEL_PATTERN
from runtimepy.mixins.regex import RegexMixin as _RegexMixin
from runtimepy.primitives.int import UnsignedInt as _UnsignedInt
from runtimepy.registry.name import RegistryKey as _RegistryKey


class BitFieldBase:
    """A simple bit-field implementation."""

    def __init__(
        self,
        raw: _UnsignedInt,
        index: int,
        width: int,
        commandable: bool = False,
        description: str = None,
    ) -> None:
        """Initialize this bit-field."""

        self.raw = raw
        self.index = index
        self.commandable = commandable
        self.description = description

        # Compute a bit-mask for this field.
        self.width = width
        self.mask = (2**self.width) - 1
        self.shifted_mask = self.mask << self.index

    def where_str(self) -> str:
        """
        Get a simple string representing the bit locations this field occupies.
        """

        result = ""

        for idx in range(self.raw.size * 8):
            val = 1 << idx
            if val & self.shifted_mask:
                result += "^"
            else:
                result += "-"

        return result

    def __call__(self, val: int = None) -> int:
        """
        Set (or get) the underlying value of this field. Return the actual
        value of the field.
        """

        # Apply the field mask.
        result: int
        if val is not None:
            result = val & self.mask

            # Get the underlying value and apply the new value.
            self.raw.value = (self.raw.value & ~self.shifted_mask) | (
                result << self.index
            )
        else:
            result = _cast(
                int, (self.raw.value & self.shifted_mask) >> self.index
            )

        return result

    def invert(self) -> int:
        """Invert the value of this field and return the result."""
        return self(~self())


class BitField(BitFieldBase, _RegexMixin, _EnumMixin):
    """A class managing a portion of an unsigned-integer primitive."""

    name_regex = _CHANNEL_PATTERN

    def __init__(
        self,
        name: str,
        raw: _UnsignedInt,
        index: int,
        width: int,
        enum: _RegistryKey = None,
        commandable: bool = False,
        description: str = None,
    ) -> None:
        """Initialize this bit-field."""

        super().__init__(
            raw, index, width, commandable=commandable, description=description
        )

        # Verify bit-field parameters.
        assert (
            raw.kind.is_integer
        ), f"Can't create a bit field with {raw.kind}!"
        assert (
            index < raw.kind.bits
        ), f"Field can't start at {index} for {raw.kind}!"
        assert (
            width <= raw.kind.bits
        ), f"Field can't be {width}-bits wide for {raw.kind}!"

        assert self.validate_name(name), f"Invalid name '{name}'!"
        self.name = name
        self._enum = enum

    def asdict(self) -> _JsonObject:
        """Get this field as a dictionary."""

        result: _JsonObject = {
            "name": self.name,
            "index": self.index,
            "width": self.width,
            "value": self(),
        }
        if self.is_enum:
            result["enum"] = self.enum
        if self.commandable:
            result["commandable"] = True
        return result


class BitFlag(BitField):
    """A bit field that is always a single bit."""

    def __init__(
        self,
        name: str,
        raw: _UnsignedInt,
        index: int,
        enum: _RegistryKey = None,
        commandable: bool = False,
        description: str = None,
    ) -> None:
        """Initialize this bit flag."""

        super().__init__(
            name,
            raw,
            index,
            1,
            enum=enum,
            commandable=commandable,
            description=description,
        )

    def clear(self) -> None:
        """Clear this field."""
        self(val=0)

    def set(self, val: bool = True) -> None:
        """Set this flag."""
        self(val=int(val))

    def get(self) -> bool:
        """Get the value of this flag."""
        return bool(self())
