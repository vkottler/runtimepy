"""
A module for implementing arrays of arbitrary primitives.
"""

# built-in
from copy import copy as _copy
from struct import pack as _pack
from struct import unpack as _unpack
from typing import BinaryIO as _BinaryIO
from typing import Dict as _Dict
from typing import List as _List
from typing import NamedTuple
from typing import cast as _cast

# internal
from runtimepy.primitives import AnyPrimitive as _AnyPrimitive
from runtimepy.primitives.byte_order import (
    DEFAULT_BYTE_ORDER as _DEFAULT_BYTE_ORDER,
)
from runtimepy.primitives.byte_order import ByteOrder as _ByteOrder


class ArrayFragmentSpec(NamedTuple):
    """Information that can be used to construct an array fragment."""

    index_start: int
    index_end: int
    byte_start: int
    byte_end: int


class PrimitiveArray:
    """A class for managing primitives as arrays."""

    def __init__(
        self,
        *primitives: _AnyPrimitive,
        byte_order: _ByteOrder = _DEFAULT_BYTE_ORDER,
        fragments: _List[ArrayFragmentSpec] = None,
    ) -> None:
        """Initialize this primitive array."""

        self._primitives: _List[_AnyPrimitive] = []
        self.byte_order = byte_order
        self._format: str = byte_order.fmt
        self.size: int = 0

        # Keep track of a quick lookup for converting between element indices
        # and byte indices.
        self._bytes_to_index: _Dict[int, int] = {0: 0}
        self._index_to_bytes: _Dict[int, int] = {0: 0}

        # Add initial items.
        for item in primitives:
            self.add(item)

        self._fragments: _List["PrimitiveArray"] = []
        self._fragment_specs: _List[ArrayFragmentSpec] = []

        # Create array fragments from the specifications.
        if fragments is None:
            fragments = []
        for spec in fragments:
            self._add_fragment(spec)

    @property
    def num_fragments(self) -> int:
        """Get the number of fragments belonging to this array."""
        return len(self._fragments)

    def fragment(self, index: int) -> "PrimitiveArray":
        """A simple accessor for fragments."""
        return self._fragments[index]

    def _create_fragment(self, spec: ArrayFragmentSpec) -> "PrimitiveArray":
        """Create a new array fragment from a fragment specification."""

        return PrimitiveArray(
            *self._primitives[spec.index_start : spec.index_end],
            byte_order=self.byte_order,
        )

    def _index_fragment_spec(
        self, start: int, end: int = -1
    ) -> ArrayFragmentSpec:
        """Create an array-fragment specification from array indices."""

        # Allow '-1' to include all elements to the right.
        if end == -1:
            end = len(self._primitives)

        assert end > start

        # The 'byte_at_index' calls sufficiently validate the inputs.
        return ArrayFragmentSpec(
            start, end, self.byte_at_index(start), self.byte_at_index(end)
        )

    def _byte_fragment_spec(
        self, start: int, end: int = -1
    ) -> ArrayFragmentSpec:
        """Create an array-fragment specification from byte indices."""

        # Allow '-1' to include all bytes to the right.
        if end == -1:
            end = self.byte_at_index(len(self._primitives))

        assert end > start

        # The 'index_at_byte' calls sufficiently validate the inputs.
        return ArrayFragmentSpec(
            self.index_at_byte(start), self.index_at_byte(end), start, end
        )

    def _add_fragment(self, spec: ArrayFragmentSpec) -> int:
        """Add a new array fragment from a fragment specification."""

        # The index of the new fragment will be equivalent to the current
        # length.
        result = len(self._fragments)

        self._fragment_specs.append(spec)
        self._fragments.append(self._create_fragment(spec))
        return result

    def fragment_from_indices(self, start: int, end: int = -1) -> int:
        """
        Create a new array fragment from primitive-member indices and return
        the fragment index.
        """
        return self._add_fragment(self._index_fragment_spec(start, end))

    def fragment_from_byte_indices(self, start: int, end: int = -1) -> int:
        """
        Create a new array fragment from byte indices and return the fragment
        index.
        """
        return self._add_fragment(self._byte_fragment_spec(start, end))

    def byte_at_index(self, index: int) -> int:
        """
        Get the byte index that a primitive at the provided index starts at.
        This can also be thought of as the size of the array leading up to
        the element at this index.
        """
        return self._index_to_bytes[index]

    def index_at_byte(self, count: int) -> int:
        """Determine the array index that a byte index lands on."""
        return self._bytes_to_index[count]

    def __copy__(self) -> "PrimitiveArray":
        """Make a copy of this primitive array."""

        return PrimitiveArray(
            *[_cast(_AnyPrimitive, x.copy()) for x in self._primitives],
            byte_order=self.byte_order,
            fragments=_copy(self._fragment_specs),
        )

    def copy(self) -> "PrimitiveArray":
        """A simple wrapper for copy."""
        return _copy(self)

    def __getitem__(self, index: int) -> _AnyPrimitive:
        """Access underlying primitives by index."""
        return self._primitives[index]

    def add(self, primitive: _AnyPrimitive) -> int:
        """Add another primitive to manage."""

        self._primitives.append(primitive)
        self._format += primitive.kind.format
        self.size += primitive.size

        # Add tracking information for the current tail.
        curr_idx = len(self._primitives)
        self._bytes_to_index[self.size] = curr_idx
        self._index_to_bytes[curr_idx] = self.size

        return self.size

    def __bytes__(self) -> bytes:
        """Get this primitive array as a bytes instance."""

        return _pack(self._format, *(x.value for x in self._primitives))

    def fragment_bytes(self, index: int) -> bytes:
        """Get bytes from a fragment."""
        return bytes(self._fragments[index])

    def to_stream(self, stream: _BinaryIO) -> int:
        """Write this array to a stream."""

        stream.write(bytes(self))
        return self.size

    def update(self, data: bytes) -> None:
        """Update primitive values from a bytes instance."""

        for primitive, item in zip(
            self._primitives, _unpack(self._format, data)
        ):
            primitive.value = item

    def update_fragment(self, index: int, data: bytes) -> None:
        """Update a fragment by index."""
        self._fragments[index].update(data)

    def from_stream(self, stream: _BinaryIO) -> int:
        """Update this array from a stream."""

        self.update(stream.read(self.size))
        return self.size
