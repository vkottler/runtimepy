"""
Common name manipulations.
"""

# built-in
import re as _re
from typing import Any as _Any


def obj_class_to_snake(class_obj: _Any) -> str:
    """Convert a CamelCase named class to a snake_case String."""

    return to_snake(class_obj.__class__.__name__)


def to_snake(name: str) -> str:
    """Convert a CamelCase String to snake_case."""

    name = _re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return _re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()
