"""
A module containing shared interfaces for HTTP.
"""

# built-in
from abc import ABC, abstractmethod
import http
from typing import Optional, TextIO, Union

# third-party
from vcorelib import DEFAULT_ENCODING
from vcorelib.logging import LoggerType

HTTPMethodlike = Union[str, http.HTTPMethod]
HEADER_LINESEP = "\r\n"


def normalize_method(data: HTTPMethodlike) -> http.HTTPMethod:
    """Normalize HTTP method data."""

    if not isinstance(data, http.HTTPMethod):
        data = http.HTTPMethod[data]
    return data


class HeadersMixin(ABC):
    """A class implementing a mixin for HTTP header fields."""

    def __init__(self, lines: list[str] = None) -> None:
        """Initialize this instance."""

        self.headers: dict[str, str] = {}
        if lines:
            for header_raw in lines:
                key, value = header_raw.split(":", maxsplit=1)
                self[key] = value

    def __getitem__(self, key: str) -> str:
        """Get a header key."""
        return self.headers[key.lower()]

    def __setitem__(self, key: str, value: str) -> None:
        """Set a header key."""
        self.headers[key.lower()] = value.strip()

    def get(self, key: str, default: str = None) -> Optional[str]:
        """Get a possible header value."""
        return self.headers.get(key.lower(), default)

    @property
    def content_length(self) -> int:
        """Get a value for context length."""
        return int(self.get("content-length", "0"))  # type: ignore

    def write_field_lines(self, stream: TextIO) -> None:
        """Write field lines to a stream."""

        for key, value in self.headers.items():
            stream.write(f"{key}: {value}")
            stream.write(HEADER_LINESEP)

    @abstractmethod
    def from_lines(self, lines: list[str]) -> None:
        """Update this request from line data."""

    @abstractmethod
    def log(self, logger: LoggerType, out: bool, **kwargs) -> None:
        """Log information about this response header."""

    @abstractmethod
    def __str__(self) -> str:
        """Get this response as a string."""

    def __bytes__(self) -> bytes:
        """Get this instances as bytes."""
        return str(self).encode(encoding=DEFAULT_ENCODING)
