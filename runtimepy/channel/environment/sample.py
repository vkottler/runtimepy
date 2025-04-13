"""
Interfaces for working with example environment configurations.
"""

# built-in
from random import randint, random

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.enum import RuntimeEnum
from runtimepy.primitives import Uint8
from runtimepy.primitives.field import BitField, BitFlag


def sample_int_enum(
    env: ChannelEnvironment, name: str = "SampleEnum"
) -> RuntimeEnum:
    """A sample integer enumeration."""

    return env.enum(
        name,
        "int",
        items={
            "zero": 0,
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
        },
    )


def long_name_int_enum(
    env: ChannelEnvironment,
    name: str = "InsanelyLongEnumNameForTesting",
    channel: str = "sample_enum",
) -> RuntimeEnum:
    """Add an integer enumeration with a long name."""

    result = env.enum(
        name,
        "int",
        {
            "very_long_member_name_0": 0,
            "very_long_member_name_1": 1,
            "very_long_member_name_2": 2,
            "very_long_member_name_3": 3,
        },
    )

    if channel:
        env.int_channel(
            channel,
            commandable=True,
            enum="InsanelyLongEnumNameForTesting",
            description="A sample long-enum-name channel.",
        )

    return result


def sample_bool_enum(
    env: ChannelEnvironment, name: str = "OnOff", channel: str = "sample_state"
) -> RuntimeEnum:
    """A sample boolean enumeration."""

    result = env.enum(name, "bool", {"On": True, "Off": False})

    if channel:
        env.bool_channel(
            channel,
            commandable=True,
            enum="OnOff",
            description="A sample on-off state channel.",
        )

    return result


def sample_fields(env: ChannelEnvironment, enum: str = "SampleEnum") -> None:
    """Add sample bit-fields to an environment."""

    with env.names_pushed("fields"):
        prim = Uint8()
        env.int_channel("raw", prim)

        # Add a bit field and flag.
        env.add_field(BitFlag(env.namespace(name="flag1"), prim, 0))
        env.add_field(
            BitFlag(
                env.namespace(name="flag2"),
                prim,
                1,
                commandable=True,
                description="Sample bit flag.",
            )
        )
        env.add_field(
            BitField(
                env.namespace(name="field1"),
                prim,
                2,
                2,
                enum=enum if enum else None,
                commandable=True,
                description="Sample bit field.",
            )
        )
        env.add_field(
            BitField(
                env.namespace(name="field2"), prim, 4, 4, commandable=True
            )
        )


def sample_float(
    env: ChannelEnvironment,
    channel: str = "sample_float",
    kind: str = "double",
) -> None:
    """Add a sample floating-point channel."""

    env.float_channel(
        channel,
        kind,
        commandable=True,
        description="A sample floating-point member.",
    )


def sample_env(env: ChannelEnvironment = None) -> ChannelEnvironment:
    """Register sample enumerations and channels to an environment."""

    if env is None:
        env = ChannelEnvironment()

    # Register an enum.
    sample_int_enum(env)

    # Boolean enumeration.
    sample_bool_enum(env)

    long_name_int_enum(env)
    sample_float(env)

    for name in ["a", "b", "c"]:
        with env.names_pushed(name):
            sample_fields(env)

            for i in range(10):
                with env.names_pushed(str(i)):
                    env.float_channel("random", "double")
                    env.int_channel("enum", enum="SampleEnum")
                    env.int_channel(
                        "really_really_long_enum",
                        enum="InsanelyLongEnumNameForTesting",
                        commandable=True,
                        default=2,
                    )
                    env.bool_channel("bool", default=True, commandable=True)
                    env.int_channel("int", commandable=True)
                    env.int_channel(
                        "scaled_int", commandable=True, scaling=[1.0, 2.0]
                    )
                    env.int_channel(
                        "scaled_float",
                        commandable=True,
                        scaling=[2.0, 3.0],
                    )

    return env


def poll_sample_env(env: ChannelEnvironment) -> None:
    """Register sample enumerations and channels to an environment."""

    # Update local channels.
    for name in ["a", "b", "c"]:
        for i in range(10):
            name_string = name + "." + str(i)
            env.set(f"{name_string}.enum", randint(0, 10))
            env.set(f"{name_string}.bool", i % 2 == 0)

            for chan in ["random"]:
                env.set(f"{name_string}.{chan}", random())
