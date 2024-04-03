"""
A module implementing interfaces for HTTP headers.
"""

# built-in
import http
from io import StringIO
import logging

# third-party
from vcorelib.logging import LoggerType

# internal
from runtimepy.net.http.common import (
    HEADER_LINESEP,
    HeadersMixin,
    HTTPMethodlike,
    normalize_method,
)
from runtimepy.net.http.request_target import RequestTarget
from runtimepy.net.http.version import (
    DEFAULT_MAJOR,
    DEFAULT_MINOR,
    HttpVersion,
)


class RequestHeader(HeadersMixin):
    """A class implementing an HTTP-request header."""

    def __init__(
        self,
        method: HTTPMethodlike = http.HTTPMethod.GET,
        target: str = "/",
        major: int = DEFAULT_MAJOR,
        minor: int = DEFAULT_MINOR,
    ) -> None:
        """Initialize this instance."""

        self.method = normalize_method(method)
        self.target = RequestTarget(self.method, target)
        self.version = HttpVersion.create(major, minor)
        HeadersMixin.__init__(self)

    def from_lines(self, lines: list[str]) -> None:
        """Update this request from line data."""

        assert lines

        method_raw, request_target_raw, version_raw = lines[0].split(" ")

        self.method = normalize_method(method_raw)
        self.target = RequestTarget(self.method, request_target_raw)
        self.version = HttpVersion(version_raw)
        HeadersMixin.__init__(self, lines[1:])

    def log(
        self, logger: LoggerType, out: bool, level: int = logging.DEBUG
    ) -> None:
        """Log information about this request header."""

        logger.log(
            level,
            "(%s request) %s - %s",
            "outgoing" if out else "incoming",
            self.request_line,
            self.headers,
        )

    @property
    def request_line(self) -> str:
        """Get this response's status line."""
        return " ".join([self.method, str(self.target.raw), str(self.version)])

    def __str__(self) -> str:
        """Get this request as a string."""

        with StringIO() as stream:
            stream.write(self.request_line)
            stream.write(HEADER_LINESEP)
            self.write_field_lines(stream)
            stream.write(HEADER_LINESEP)

            return stream.getvalue()
