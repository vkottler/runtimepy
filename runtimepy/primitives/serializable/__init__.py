"""
A module defining an interface for serializable objects.
"""

# built-in
from typing import Dict

# internal
from runtimepy.primitives.serializable.base import Serializable
from runtimepy.primitives.serializable.fixed import FixedChunk
from runtimepy.primitives.serializable.prefixed import PrefixedChunk

SerializableMap = Dict[str, Serializable]
__all__ = ["Serializable", "SerializableMap", "FixedChunk", "PrefixedChunk"]
