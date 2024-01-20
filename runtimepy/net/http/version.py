"""
A module implementing an interface for HTTP versions.
"""


class HttpVersion:
    """A class implementing a simple HTTP version interface."""

    def __init__(self, version_raw: str) -> None:
        """Initialize this instance."""

        http_str, version = version_raw.split("/")
        assert http_str == "HTTP"
        version_major, version_minor = version.split(".")
        self.major = int(version_major)
        self.minor = int(version_minor)

    def __str__(self) -> str:
        """Get this instance as a string."""
        return f"HTTP/{self.major}.{self.minor}"
