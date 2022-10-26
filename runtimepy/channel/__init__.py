"""
A module implementing a basic channel interface.
"""

# internal
from runtimepy.registry.item import RegistryItem as _RegistryItem


class Channel(_RegistryItem):
    """An interface for an individual channel."""
