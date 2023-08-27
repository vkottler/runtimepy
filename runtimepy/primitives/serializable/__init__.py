"""
A module defining an interface for serializable objects.
"""

# internal
from runtimepy.primitives.serializable.base import Serializable
from runtimepy.primitives.serializable.fixed import FixedChunk

__all__ = ["Serializable", "FixedChunk"]
