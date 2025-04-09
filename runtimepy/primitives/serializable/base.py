"""
A module defining a base interface fore serializable objects.
"""

# built-in
from abc import ABC, abstractmethod
from copy import copy as _copy
from io import BytesIO as _BytesIO
from typing import BinaryIO as _BinaryIO
from typing import TypeVar

# third-party
from vcorelib import DEFAULT_ENCODING

# internal
from runtimepy.primitives.byte_order import (
    DEFAULT_BYTE_ORDER as _DEFAULT_BYTE_ORDER,
)
from runtimepy.primitives.byte_order import ByteOrder as _ByteOrder

T = TypeVar("T", bound="Serializable")


class Serializable(ABC):
    """An interface for serializable objects."""

    size: int

    def __init__(
        self,
        byte_order: _ByteOrder = _DEFAULT_BYTE_ORDER,
        chain: T = None,
    ) -> None:
        """Initialize this instance."""

        if not hasattr(self, "size"):
            self.size = 0

        self.byte_order = byte_order
        self.chain = chain

    def length(self) -> int:
        """Get the full length of this chain."""

        result = self.size
        if self.chain is not None:
            result += self.chain.length()
        return result

    def resolve_alias(self, alias: str = None) -> str:
        """Resolve a possible alias string."""

        if not alias:
            alias = getattr(self, "alias") or self.__class__.__name__
        return alias

    def length_trace(self, alias: str = None) -> str:
        """Get a length-tracing string for this instance."""

        current = f"{self.resolve_alias(alias=alias)}({self.size})"
        if self.chain is not None:
            current += " -> " + self.chain.length_trace()
        return current

    @property
    def end(self) -> "Serializable":
        """Get the end of this chain."""

        result = self
        if self.chain is not None:
            result = self.chain.end
        return result

    @abstractmethod
    def _copy_impl(self: T) -> T:
        """Make a copy of this instance."""

    def copy_without_chain(self: T) -> T:
        """A method for copying instances without chain references."""

        orig = self._copy_impl()
        orig.byte_order = self.byte_order
        return orig

    def __copy__(self: T) -> T:
        """Make a copy of this serializable."""

        result = self.copy_without_chain()

        if self.chain is not None and result.chain is None:
            result.assign(self.chain.copy())

        return result

    def copy(self: T) -> T:
        """Create a copy of a serializable instance."""
        return _copy(self)

    @abstractmethod
    def __bytes__(self) -> bytes:
        """Get this serializable as a bytes instance."""

    def to_stream(self, stream: _BinaryIO) -> int:
        """Write this serializable to a stream."""

        stream.write(bytes(self))
        result = self.size

        if self.chain is not None:
            result += self.chain.to_stream(stream)

        return result

    def chain_bytes(self) -> bytes:
        """Get the fully encoded chain."""
        with _BytesIO() as stream:
            self.to_stream(stream)
            return stream.getvalue()

    def __eq__(self, other) -> bool:
        """Equivalent if full byte chains are equal."""

        result = False
        if isinstance(other, Serializable):
            result = self.chain_bytes() == other.chain_bytes()
        return result

    def update_with(self: T, other: T, timestamp_ns: int = None) -> int:
        """Update this instance from another of the same type."""

        return self.update_chain(
            other.chain_bytes(), timestamp_ns=timestamp_ns
        )

    @abstractmethod
    def update(self, data: bytes, timestamp_ns: int = None) -> int:
        """Update this serializable from a bytes instance."""

    def update_str(self, data: str, timestamp_ns: int = None) -> int:
        """Update this serializable from string data."""

        return self.update(
            data.encode(encoding=DEFAULT_ENCODING), timestamp_ns=timestamp_ns
        )

    def _from_stream(self, stream: _BinaryIO, timestamp_ns: int = None) -> int:
        """Update just this instance from a stream."""

        return self.update(stream.read(self.size), timestamp_ns=timestamp_ns)

    def from_stream(self, stream: _BinaryIO, timestamp_ns: int = None) -> int:
        """Update this serializable from a stream."""

        result = self._from_stream(stream, timestamp_ns=timestamp_ns)

        if self.chain is not None:
            result += self.chain.from_stream(stream, timestamp_ns=timestamp_ns)

        return result

    def update_chain(self, data: bytes, timestamp_ns: int = None) -> int:
        """Update this serializable from a bytes instance."""

        with _BytesIO(data) as stream:
            return self.from_stream(stream, timestamp_ns=timestamp_ns)

    def assign(self, chain: T) -> None:
        """Assign a next serializable."""

        assert self.chain is None, self.chain
        # mypy regression?
        self.chain = chain  # type: ignore

    def add_to_end(self, chain: T, array_length: int = None) -> list[T]:
        """Add a new serializable to the end of this chain."""

        result = []

        # Copy the chain element before it becomes part of the current chain if
        # an array is created.
        copy_base = None
        if array_length is not None:
            copy_base = chain.copy()

        self.end.assign(chain)
        result.append(chain)

        # Add additional array elements as copies.
        if array_length is not None:
            assert copy_base is not None
            for _ in range(array_length - 1):
                inst = copy_base.copy()
                self.end.assign(inst)
                result.append(inst)

        return result
