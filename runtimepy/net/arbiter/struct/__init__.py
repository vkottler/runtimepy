"""
A module implementing a runtime data structure interface.
"""

# built-in
from abc import ABC as _ABC
from abc import abstractmethod as _abstractmethod

# internal
from runtimepy.channel.environment.sample import poll_sample_env, sample_env
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.struct import RuntimeStructBase


class RuntimeStruct(RuntimeStructBase, _ABC):
    """A class implementing a base runtime structure."""

    @_abstractmethod
    async def build(self, app: AppInfo) -> None:
        """Build a struct instance's channel environment."""


class SampleStruct(RuntimeStruct):
    """A sample runtime structure."""

    async def build(self, app: AppInfo) -> None:
        """Build a struct instance's channel environment."""

        del app
        sample_env(self.env)

    def poll(self) -> None:
        """
        A method that other runtime entities can call to perform canonical
        updates to this struct's environment.
        """
        poll_sample_env(self.env)
