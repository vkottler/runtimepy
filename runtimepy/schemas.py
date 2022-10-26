"""
A module for working with schemas belonging to this package.
"""

# built-in
from functools import lru_cache as _lru_cache

# third-party
from vcorelib.schemas import JsonSchemaMap as _JsonSchemaMap

# internal
from runtimepy import PKG_NAME


@_lru_cache(1)
def json_schemas(package: str = PKG_NAME) -> _JsonSchemaMap:
    """Load JSON schemas from this package."""
    return _JsonSchemaMap.from_package(package)
