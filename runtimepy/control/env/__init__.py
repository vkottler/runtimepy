"""
A module implementing runtime-environment registration routines for commonly
used control channel types.
"""

# built-in
from typing import TypeVar

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.primitives import AnyPrimitive
from runtimepy.ui.controls import Controlslike

T = TypeVar("T", bound=AnyPrimitive)


def phase_angle(
    env: ChannelEnvironment,
    primitive: type[T],
    name: str = "phase_angle",
    controls: Controlslike = "phase",
    **kwargs,
) -> T:
    """Create a phase-angle channel."""

    prim = primitive()
    env.channel(name, prim, commandable=True, controls=controls, **kwargs)
    return prim  # type: ignore


def amplitude(
    env: ChannelEnvironment,
    primitive: type[T],
    name: str = "amplitude",
    controls: Controlslike = "amplitude",
    **kwargs,
) -> T:
    """Create an amplitude channel."""

    prim = primitive()
    env.channel(name, prim, commandable=True, controls=controls, **kwargs)
    return prim  # type: ignore


def steps(
    env: ChannelEnvironment,
    primitive: type[T],
    name: str = "steps",
    controls: Controlslike = "steps",
    **kwargs,
) -> T:
    """Create a steps channel."""

    prim = primitive()
    env.channel(name, prim, commandable=True, controls=controls, **kwargs)
    return prim  # type: ignore
