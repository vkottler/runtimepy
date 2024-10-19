"""
A module implementing package utilities.
"""

# built-in
from os import sep
from pathlib import Path
from typing import Iterator, Union

# third-party
from vcorelib.paths import normalize

ROOT_PATH = Path(sep)


def normalize_root(*src_parts: Union[str, Path]) -> Path:
    """Make paths absolute that aren't. Useful for HTTP-request pathing."""

    result = normalize(*src_parts)
    if not result.is_absolute():
        result = ROOT_PATH.joinpath(result)
    return result


class Identifier:
    """A simple message indentifier interface."""

    def __init__(self) -> None:
        """Initialize this instance."""
        self.curr_id: int = 1
        self.scale = 2

    def __call__(self) -> int:
        """Get the next identifier."""
        curr = self.curr_id
        self.curr_id += self.scale
        return curr


def path_has_part(path: str, key: str = "json") -> bool:
    """Determine if a key appears as a part of a path."""

    # Ignore '/' component (intended for URI paths).
    return key in path.split("/")[1:]


def parse_path_parts(path: str, key: str = "json") -> Iterator[str]:
    """
    Parse a path such that all parts appearing after a possible 'key' appears
    are yielded.
    """

    key_found = False

    # Ignore '/' component (intended for URI paths).
    for item in path.split("/")[1:]:
        if key_found:
            yield item
        elif item == key:
            key_found = True
