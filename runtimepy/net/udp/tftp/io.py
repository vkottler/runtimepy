"""
A module implementing I/O utilities related to tftp transactions.
"""

# built-in
from pathlib import Path
from typing import Iterator


def tftp_chunks(
    path: Path, max_block_size: int, mode: str = "rb"
) -> Iterator[bytes]:
    """Iterate over file chunks."""

    # Gather all file chunks.
    prev_length = 0
    with path.open(mode) as path_fd:
        keep_going = True
        while keep_going:
            data = path_fd.read(max_block_size)
            keep_going = bool(data)

            # Only yield non-empty payloads (handle termination
            # separately).
            if keep_going:
                yield data
                prev_length = len(data)

    # Terminate transaction if necessary.
    if prev_length == 0 or prev_length >= max_block_size:
        yield bytes()
