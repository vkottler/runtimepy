"""
A module implementing a simple request-target (3.2) interface.
"""

# built-in
import http
from typing import Optional, Tuple

PathMaybeQuery = Tuple[str, Optional[str]]


class RequestTarget:
    """A class implementing HTTP's request-target definition."""

    def __init__(
        self, method: http.HTTPMethod, request_target_raw: str
    ) -> None:
        """Initialize this instance."""

        self.raw = request_target_raw

        # Host and port.
        self.authority_form: Optional[Tuple[str, int]] = None

        # Path and optional query.
        self.origin_form: Optional[PathMaybeQuery] = None

        self.absolute_form: Optional[str] = None

        query = None

        # 3.2.4 asterisk-form
        self.asterisk_form = False
        if request_target_raw == "*":
            self.asterisk_form = True

        # 3.2.3 authority-form
        elif method == http.HTTPMethod.CONNECT:
            host, port = request_target_raw.split(":")
            self.authority_form = (host, int(port))

        # 3.2.1 origin-form
        elif request_target_raw.startswith("/"):
            parts = request_target_raw.split("?")
            path = parts[0]
            if len(parts) > 1:
                query = parts[1]
            self.origin_form = (path, query)

        # 3.2.2 absolute-form
        else:
            self.absolute_form = request_target_raw

    @property
    def path(self) -> str:
        """Get the path for this request."""

        assert self.origin_form is not None
        return self.origin_form[0]
