"""
A module implementing a channel-environment mixin for connections.
"""

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.net.connection import Connection


class ChannelEnvironmentMixin(Connection):
    """A connection mixin for including a channel environment."""

    env: ChannelEnvironment

    def init(self) -> None:
        """Initialize this instance."""

        if not hasattr(self, "env"):
            self.env = ChannelEnvironment()

            # Add metrics channels.
            with self.env.names_pushed("metrics"):
                for name, direction in [
                    ("tx", self.metrics.tx),
                    ("rx", self.metrics.rx),
                ]:
                    with self.env.names_pushed(name):
                        self.env.channel("messages", direction.messages)
                        self.env.channel(
                            "messages_rate", direction.message_rate
                        )
                        self.env.channel("bytes", direction.bytes)
                        self.env.channel("kbps", direction.kbps)
