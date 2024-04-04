"""
A module implementing a runtime data structure interface.
"""

# built-in
from abc import ABC as _ABC
from abc import abstractmethod as _abstractmethod
from logging import getLogger as _getLogger
from typing import Dict as _Dict

# internal
from runtimepy.channel.environment.command.processor import (
    ChannelCommandProcessor,
)
from runtimepy.channel.environment.sample import poll_sample_env, sample_env
from runtimepy.mixins.environment import ChannelEnvironmentMixin
from runtimepy.mixins.logging import LoggerMixinLevelControl


class RuntimeStruct(LoggerMixinLevelControl, ChannelEnvironmentMixin, _ABC):
    """A class implementing a base runtime structure."""

    auto_finalize = True

    def __init__(self, name: str) -> None:
        """Initialize this instance."""

        self.name = name
        LoggerMixinLevelControl.__init__(self, logger=_getLogger(self.name))
        ChannelEnvironmentMixin.__init__(self)
        self.setup_level_channel(self.env)
        self.command = ChannelCommandProcessor(self.env, self.logger)

    @_abstractmethod
    def build(self) -> None:
        """Build a struct instance's channel environment."""

    def poll(self) -> None:
        """
        A method that other runtime entities can call to perform canonical
        updates to this struct's environment.
        """

    def init(self) -> None:
        """Initialize this task with application information."""

        self.build()
        if self.auto_finalize:
            self.env.finalize()


StructMap = _Dict[str, RuntimeStruct]


class SampleStruct(RuntimeStruct):
    """A sample runtime structure."""

    def build(self) -> None:
        """Build a struct instance's channel environment."""
        sample_env(self.env)

    def poll(self) -> None:
        """
        A method that other runtime entities can call to perform canonical
        updates to this struct's environment.
        """
        poll_sample_env(self.env)
