"""
A module implementing HTTP-response interfaces.
"""

# built-in
import http
from io import StringIO
import logging

# third-party
from vcorelib.logging import LoggerType

# internal
from runtimepy.net.http.common import HEADER_LINESEP, HeadersMixin
from runtimepy.net.http.version import (
    DEFAULT_MAJOR,
    DEFAULT_MINOR,
    HttpVersion,
)


class ResponseHeader(HeadersMixin):
    """A class implementing an HTTP-response header."""

    def __init__(
        self,
        major: int = DEFAULT_MAJOR,
        minor: int = DEFAULT_MINOR,
        status: http.HTTPStatus = http.HTTPStatus.OK,
        reason: str = "",
        content_type: str = "application/octet-stream",
    ) -> None:
        """Initialize this instance."""

        self.version = HttpVersion.create(major, minor)
        self.status = status
        self.reason = reason
        HeadersMixin.__init__(self)
        self["content-type"] = content_type

    def from_lines(self, lines: list[str]) -> None:
        """Update this request from line data."""

        assert lines

        status_parts = lines[0].split(" ", maxsplit=2)
        if len(status_parts) == 3:
            self.reason = status_parts[2]

        self.version = HttpVersion(status_parts[0])
        self.status = http.HTTPStatus(int(status_parts[1]))

        HeadersMixin.__init__(self, lines[1:])

    @property
    def status_line(self) -> str:
        """Get this response's status line."""

        parts = [str(self.version), str(self.status.value)]
        if self.reason:
            parts.append(self.reason)
        return " ".join(parts)

    def __str__(self) -> str:
        """Get this response as a string."""

        with StringIO() as stream:
            stream.write(self.status_line)
            stream.write(HEADER_LINESEP)
            self.write_field_lines(stream)
            stream.write(HEADER_LINESEP)

            return stream.getvalue()

    def log(self, logger: LoggerType, out: bool, **_) -> None:
        """Log information about this response header."""

        level = logging.INFO if (200 <= self.status <= 299) else logging.ERROR
        logger.debug(
            level,
            "(%s response) %s - %s",
            "outgoing" if out else "incoming",
            self.status_line,
            self.headers,
        )
