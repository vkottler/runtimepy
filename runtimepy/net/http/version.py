"""
A module implementing an interface for HTTP versions.
"""

DEFAULT_MAJOR = 1
DEFAULT_MINOR = 1


class HttpVersion:
    """A class implementing a simple HTTP version interface."""

    def __init__(self, version_raw: str) -> None:
        """Initialize this instance."""

        http_str, version = version_raw.split("/")
        assert http_str == "HTTP"
        version_major, version_minor = version.split(".")
        self.major = int(version_major)
        self.minor = int(version_minor)

    @staticmethod
    def create(
        major: int = DEFAULT_MAJOR, minor: int = DEFAULT_MINOR
    ) -> "HttpVersion":
        """Create a version instance."""
        return HttpVersion(HttpVersion.version_str(major=major, minor=minor))

    @staticmethod
    def version_str(
        major: int = DEFAULT_MAJOR, minor: int = DEFAULT_MINOR
    ) -> str:
        """Get version information as a string."""
        return f"HTTP/{major}.{minor}"

    def __str__(self) -> str:
        """Get this instance as a string."""
        return HttpVersion.version_str(major=self.major, minor=self.minor)
