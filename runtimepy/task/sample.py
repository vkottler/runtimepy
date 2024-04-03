"""
A sample task interface.
"""

# built-in
import asyncio
from random import random

# third-party
from runtimepy.net.arbiter import AppInfo
from runtimepy.net.arbiter.task import ArbiterTask, TaskFactory
from runtimepy.net.stream.json import JsonMessageConnection
from runtimepy.primitives import Uint8
from runtimepy.primitives.field import BitField, BitFlag


class SampleTask(ArbiterTask):
    """A base TUI application."""

    async def init(self, app: AppInfo) -> None:
        """Initialize this task with application information."""

        await super().init(app)

        # Register an enum.
        sample_enum = self.env.enum(
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

        self.env.enum(
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
            with self.env.names_pushed(name):
                with self.env.names_pushed("fields"):
                    prim = Uint8()
                    self.env.int_channel("raw", prim)

                    # Add a bit field and flag.
                    self.env.add_field(BitFlag("flag1", prim, 0))
                    self.env.add_field(
                        BitFlag("flag2", prim, 1, commandable=True)
                    )
                    self.env.add_field(
                        BitField(
                            "field1",
                            prim,
                            2,
                            2,
                            enum=sample_enum.id,
                            commandable=True,
                        )
                    )
                    self.env.add_field(BitField("field2", prim, 4, 4))

                for i in range(10):
                    with self.env.names_pushed(str(i)):
                        self.env.float_channel("random", "double")
                        self.env.int_channel("enum", enum="SampleEnum")
                        self.env.int_channel(
                            "really_really_long_enum",
                            enum="InsanelyLongEnumNameForTesting",
                            commandable=True,
                        )
                        self.env.bool_channel("bool")
                        self.env.int_channel("int", commandable=True)
                        self.env.int_channel(
                            "scaled_int", commandable=True, scaling=[1.0, 2.0]
                        )
                        self.env.int_channel(
                            "scaled_float",
                            commandable=True,
                            scaling=[2.0, 3.0],
                        )

    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""

        # Use this to implement / test rate-limited logging.
        with self.log_time("dispatch"):
            dispatches = self.metrics.dispatches.value % 10

            # Update local channels.
            for name in ["a", "b", "c"]:
                for i in range(10):
                    name_string = name + "." + str(i)
                    self.env.set(
                        f"{name_string}.enum", ((dispatches + i) % 10) + 1
                    )
                    self.env.set(f"{name_string}.bool", i % 2 == 0)

                    for chan in ["random"]:
                        self.env.set(f"{name_string}.{chan}", random())

            # Interact with connections.
            await asyncio.gather(
                *(
                    x.loopback()
                    for x in self.app.search(
                        pattern="client", kind=JsonMessageConnection
                    )
                )
            )

        return True


class Sample(TaskFactory[SampleTask]):
    """A TUI application factory."""

    kind = SampleTask
