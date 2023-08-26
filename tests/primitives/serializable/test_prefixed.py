"""
Test the 'primitives.serializable.prefixed' module.
"""

# built-in
from io import BytesIO
from typing import cast

# module under test
from runtimepy.primitives.serializable.prefixed import PrefixedChunk


def test_prefixed_chunk_basic():
    """Test basic interactions with a prefixed chunk."""

    end = PrefixedChunk.create("uint8")
    chunk = PrefixedChunk.create(chain=end)

    assert chunk.update_str("Hello") == 7
    assert end.update_str(", world!") == 9

    assert len(bytes(chunk)) == 7
    assert len(bytes(end)) == 9

    assert str(chunk) + str(end) == "Hello, world!"
    assert chunk.length() == 16

    chunk_copy = chunk.copy()
    end_copy: PrefixedChunk = cast(PrefixedChunk, chunk_copy.end)

    assert chunk.update_str("a") == 3
    assert end.update_str("b") == 2

    assert str(chunk_copy) + str(end_copy) == "Hello, world!"

    with BytesIO() as stream:
        assert chunk.to_stream(stream) == 5

        stream.seek(0)

        assert chunk_copy.from_stream(stream) == 5

    assert str(chunk_copy) + str(end_copy) == "ab"
    assert chunk_copy.length() == 5
