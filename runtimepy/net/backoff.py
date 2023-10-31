"""
A module implementing a simple exponential-backoff interface.
"""

# built-in
import asyncio


class ExponentialBackoff:
    """A class implementing a simple exponential-backoff handler."""

    wait: float
    attempt: int

    def __init__(
        self,
        interval: float = 0.1,
        max_sleep: float = 10.0,
        max_tries: int = 20,
    ) -> None:
        """Initialize this instance."""

        self.interval = interval
        self.max_sleep = max_sleep
        self.max_tries = max_tries
        self.reset()

    def reset(self) -> None:
        """Reset this instance's state."""

        self.wait = 0.0
        self.attempt = 0

    @property
    def give_up(self) -> bool:
        """
        Determine whether or not to give up based on the number of attempts.
        """
        return self.attempt >= self.max_tries

    async def sleep(self) -> None:
        """Sleep for the correct amount of time."""

        await asyncio.sleep(self.wait)
        self.wait = min((2 ^ self.attempt) * self.interval, self.max_sleep)
        self.attempt += 1
