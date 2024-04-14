"""
A module implementing a simple, application-result interface.
"""

# built-in
from enum import StrEnum
import logging
from typing import NamedTuple, Optional

# third-party
from vcorelib.logging import LoggerType
from vcorelib.math import nano_str


class ResultState(StrEnum):
    """Possible outcomes of an application method."""

    PASS = "pass"
    FAIL = "fail"
    NOT_RUN = "not run"
    EXCEPTION = "exception"

    def __bool__(self) -> bool:
        """Convert an enum instance to boolean."""
        return self is ResultState.PASS

    @property
    def log_level(self) -> int:
        """Get a log level for this result state."""

        if self is ResultState.NOT_RUN:
            return logging.WARNING

        return logging.INFO if bool(self) else logging.ERROR

    @staticmethod
    def from_int(data: int) -> "ResultState":
        """Create result state from an integer."""
        return ResultState.PASS if data == 0 else ResultState.FAIL


class AppResult(NamedTuple):
    """A container for application-result information."""

    method: str
    state: ResultState = ResultState.NOT_RUN
    code: Optional[int] = None
    exception: Optional[Exception] = None
    duration_ns: Optional[int] = None

    def log(
        self, overall_idx: int, stage_idx: int, logger: LoggerType
    ) -> None:
        """Log information about this result."""

        fmt = "%d.%d %s: %s"
        fmt_args = [overall_idx, stage_idx, self.method, str(self.state)]

        if self.code is not None:
            fmt += " (%d)"
            fmt_args.append(self.code)

        if self.duration_ns:
            fmt += " %ss."
            fmt_args.append(nano_str(self.duration_ns, is_time=True))

        if self.exception is not None:
            logger.exception(fmt + " -", *fmt_args, exc_info=self.exception)
        else:
            logger.log(self.state.log_level, fmt, *fmt_args)


# App methods can run in parallel, group them as a stage.
StageResult = list[AppResult]


def log_stage(
    overall_idx: int, result: StageResult, logger: LoggerType = None
) -> bool:
    """Log the results of a stage."""

    success = True

    for idx, instance in enumerate(result):
        if logger is not None:
            instance.log(overall_idx, idx, logger)

        success &= bool(instance.state)

    return success


# The overall application's result is a collection of stage results.
OverallResult = list[StageResult]


def results(result: OverallResult, logger: LoggerType = None) -> bool:
    """Log overall results."""

    if logger is not None:
        logger.info("========================================")

    success = True

    for idx, instance in enumerate(result):
        success &= log_stage(idx, instance, logger=logger)

    if logger is not None:
        logger.info("========================================")

    return success
