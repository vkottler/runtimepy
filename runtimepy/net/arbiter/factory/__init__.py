"""
A module implementing an interface extension to the base connection-arbiter so
that methods that create connections can be registered by name.
"""

# internal
from runtimepy.net.arbiter.factory.connection import (
    ConnectionFactory,
    FactoryConnectionArbiter,
)

__all__ = ["ConnectionFactory", "FactoryConnectionArbiter"]
