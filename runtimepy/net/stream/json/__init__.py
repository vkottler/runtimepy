"""
A module implementing a JSON message connection interface.
"""

# internal
from runtimepy.net.stream.json.base import JsonMessageConnection
from runtimepy.net.stream.json.handlers import event_wait

__all__ = ["JsonMessageConnection", "event_wait"]
