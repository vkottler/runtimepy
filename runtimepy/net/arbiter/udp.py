"""
A module implementing a basic UDP connection factory that can be extended.
"""

# built-in
from typing import Generic as _Generic
from typing import TypeVar as _TypeVar

# internal
from runtimepy.net.arbiter.factory import (
    ConnectionFactory as _ConnectionFactory,
)
from runtimepy.net.connection import Connection as _Connection
from runtimepy.net.udp.connection import UdpConnection as _UdpConnection

T = _TypeVar("T", bound=_UdpConnection)


class UdpConnectionFactory(
    _ConnectionFactory, _Generic[T]
):  # pylint: disable=abstract-method
    """A class implementing a basic UDP connection factory."""

    kind: type[T]

    async def client(self, name: str, *args, **kwargs) -> _Connection:
        """Create a client connection."""

        del name
        assert not [*args], "Only keyword arguments are used!"
        return await self.kind.create_connection(**kwargs)
