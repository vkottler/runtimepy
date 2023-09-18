"""
A module implementing a class with a simple finalize interface.
"""

# built-in
from asyncio import Event


class FinalizeMixin:
    """A class implementing a simple finalize interface."""

    def __init__(self, event: Event = None) -> None:
        """Initialize this instance."""

        if event is None:
            event = Event()
        self._finalized = event

    async def wait_finalized(self) -> None:
        """Wait for this instance to be finalized."""
        await self._finalized.wait()

    @property
    def finalized(self) -> bool:
        """Determine if this instance is finalized or not."""
        return self._finalized.is_set()

    def finalize(self, strict: bool = True) -> None:
        """Finalize this instance."""

        if strict:
            assert not self.finalized, "Instance already finalized!"

        self._finalized.set()
