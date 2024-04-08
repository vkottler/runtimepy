"""
A module implementing an HTTP-header processing state interface.
"""

# built-in
from dataclasses import dataclass
from typing import Optional, TypeVar

# third-party
from vcorelib import DEFAULT_ENCODING
from vcorelib.io import ByteFifo

# internal
from runtimepy.net.http.common import HeadersMixin

T = TypeVar("T", bound=HeadersMixin)


@dataclass
class HeaderProcessingState:
    """A container for header-related processing state."""

    lines: list[str]
    line: str

    @staticmethod
    def create() -> "HeaderProcessingState":
        """Create a default instance."""
        return HeaderProcessingState([], "")

    def service(self, buffer: ByteFifo, kind: type[T]) -> Optional[T]:
        """
        Continue processing the input fifo as if it contains request-header
        data.
        """

        result = None

        while result is None and buffer.size:
            curr_raw = buffer.pop(1)
            if curr_raw is not None:
                curr = curr_raw.decode(encoding=DEFAULT_ENCODING)

                # Any '\r\n' sequence signifies the end of a header line.
                if curr == "\n":
                    if self.line:
                        self.lines.append(self.line)
                        self.line = ""

                    # Two sequences in a row signifies the end of the header
                    # section.
                    else:
                        result = kind()
                        result.from_lines(self.lines)
                        self.lines = []

                elif curr != "\r":
                    self.line += curr

        return result
