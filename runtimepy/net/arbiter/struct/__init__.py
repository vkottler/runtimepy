"""
A module implementing a runtime data structure interface.
"""

# built-in
from abc import ABC as _ABC

# internal
from runtimepy.channel.environment.sample import poll_sample_env, sample_env
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.struct import RuntimeStructBase


class RuntimeStruct(RuntimeStructBase, _ABC):
    """A class implementing a base runtime structure."""

    def init_env(self) -> None:
        """Initialize this sample environment."""

    async def build(self, app: AppInfo) -> None:
        """Build a struct instance's channel environment."""

        del app
        self.init_env()


class SampleStruct(RuntimeStruct):
    """A sample runtime structure."""

    def init_env(self) -> None:
        """Initialize this sample environment."""
        sample_env(self.env)

    def poll(self) -> None:
        """
        A method that other runtime entities can call to perform canonical
        updates to this struct's environment.
        """
        poll_sample_env(self.env)
