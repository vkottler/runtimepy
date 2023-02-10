"""
A module for working with schemas belonging to this package.
"""

# built-in
from functools import lru_cache as _lru_cache
from typing import Optional as _Optional

# third-party
from vcorelib.dict.codec import DictCodec as _DictCodec
from vcorelib.schemas.base import SchemaMap as _SchemaMap
from vcorelib.schemas.json import JsonSchemaMap as _JsonSchemaMap

# internal
from runtimepy import PKG_NAME


@_lru_cache(1)
def json_schemas(package: str = PKG_NAME) -> _JsonSchemaMap:
    """Load JSON schemas from this package."""
    return _JsonSchemaMap.from_package(package)


class RuntimepyDictCodec(_DictCodec):
    """
    A simple wrapper for package classes that want to implement DictCodec.
    """

    default_schemas: _Optional[_SchemaMap] = json_schemas()
