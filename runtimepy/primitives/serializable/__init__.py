"""
A module defining an interface for serializable objects.
"""

# internal
from runtimepy.primitives.serializable.base import Serializable
from runtimepy.primitives.serializable.fixed import FixedChunk
from runtimepy.primitives.serializable.prefixed import PrefixedChunk

SerializableMap = dict[str, list[Serializable]]
__all__ = ["Serializable", "SerializableMap", "FixedChunk", "PrefixedChunk"]
