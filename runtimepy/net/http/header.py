"""
A module implementing interfaces for HTTP headers.
"""

# built-in
import http

# third-party
from vcorelib.logging import LoggerType

# internal
from runtimepy.net.http.request_target import RequestTarget
from runtimepy.net.http.version import HttpVersion


class HttpHeader:
    """A class implementing an HTTP header."""

    def __init__(self, lines: list[str]) -> None:
        """Initialize this instance."""

        assert lines

        method_raw, request_target_raw, version_raw = lines[0].split(" ")

        self.method = http.HTTPMethod[method_raw]
        self.target = RequestTarget(self.method, request_target_raw)
        self.version = HttpVersion(version_raw)

        self.headers: dict[str, str] = {}
        for header_raw in lines[1:]:
            key, value = header_raw.split(":", maxsplit=1)
            self[key] = value

    def __getitem__(self, key: str) -> str:
        """Get a header key."""
        return self.headers[key.lower()]

    def __setitem__(self, key: str, value: str) -> None:
        """Set a header key."""
        self.headers[key.lower()] = value.strip()

    def log(self, logger: LoggerType) -> None:
        """Log information about this request header."""

        logger.info(
            "%s - %s %s - %s",
            self.version,
            self.method,
            self.target,
            self.headers,
        )
