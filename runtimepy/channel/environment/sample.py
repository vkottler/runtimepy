"""
Interfaces for working with example environment configurations.
"""

# built-in
from random import randint, random

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.primitives import Uint8
from runtimepy.primitives.field import BitField, BitFlag


def sample_env(env: ChannelEnvironment = None) -> ChannelEnvironment:
    """Register sample enumerations and channels to an environment."""

    if env is None:
        env = ChannelEnvironment()

    # Register an enum.
    sample_enum = env.enum(
        "SampleEnum",
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

    env.enum(
        "InsanelyLongEnumNameForTesting",
        "int",
        {
            "very_long_member_name_0": 0,
            "very_long_member_name_1": 1,
            "very_long_member_name_2": 2,
            "very_long_member_name_3": 3,
        },
    )

    for name in ["a", "b", "c"]:
        with env.names_pushed(name):
            with env.names_pushed("fields"):
                prim = Uint8()
                env.int_channel("raw", prim)

                # Add a bit field and flag.
                env.add_field(BitFlag("flag1", prim, 0))
                env.add_field(
                    BitFlag(
                        "flag2",
                        prim,
                        1,
                        commandable=True,
                        description="Sample bit flag.",
                    )
                )
                env.add_field(
                    BitField(
                        "field1",
                        prim,
                        2,
                        2,
                        enum=sample_enum.id,
                        commandable=True,
                        description="Sample bit field.",
                    )
                )
                env.add_field(BitField("field2", prim, 4, 4, commandable=True))

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
