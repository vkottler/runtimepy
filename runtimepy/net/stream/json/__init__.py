"""
A module implementing a JSON message connection interface.
"""

# internal
from runtimepy.net.stream.json.base import JsonMessageConnection
from runtimepy.net.stream.json.handlers import event_wait
from runtimepy.net.stream.json.types import JsonMessage

__all__ = ["JsonMessageConnection", "event_wait", "JsonMessage"]
