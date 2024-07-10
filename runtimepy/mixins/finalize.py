"""
A module implementing a class with a simple finalize interface.
"""

# built-in
from asyncio import Event
from contextlib import contextmanager
from typing import Iterator


class FinalizeMixin:
    """A class implementing a simple finalize interface."""

    def __init__(self, event: Event = None) -> None:
        """Initialize this instance."""

        if event is None:
            event = Event()
        self._finalized = event
        self._finalized_bypass = False

    async def wait_finalized(self) -> None:
        """Wait for this instance to be finalized."""
        await self._finalized.wait()

    @property
    def finalized(self) -> bool:
        """Determine if this instance is finalized or not."""

        return False if self._finalized_bypass else self._finalized.is_set()

    def finalize(self, strict: bool = True) -> None:
        """Finalize this instance."""

        if strict:
            assert not self.finalized, "Instance already finalized!"

        self._finalized.set()

    @contextmanager
    def bypass_finalized(self) -> Iterator[None]:
        """
        Allows bypassing 'finalized' checks for specific situations. Ideally
        runtime environment entities don't rely on this, but things like
        self-describing network protocols it's difficult to resolve
        runtime-state storage needs during initialization alone.
        """

        assert not self._finalized_bypass, "Finalization already bypassed!"

        self._finalized_bypass = True
        try:
            yield
        finally:
            self._finalized_bypass = False
