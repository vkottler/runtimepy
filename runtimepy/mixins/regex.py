"""
A class mixin for classes that have a regular expression that they wish to
validate names with.
"""

# built-in
from re import Pattern as _Pattern
from re import compile as _compile

# third-party
from vcorelib.logging import LoggerType

DEFAULT_PATTERN = _compile("^[\\w\\:.-]+$")
CHANNEL_PATTERN = _compile("^[a-z0-9_.-]+$")


class RegexMixin:
    """A simple class mixin for validating names."""

    # Sub-classes can set this to validate names using a different pattern.
    name_regex: _Pattern = DEFAULT_PATTERN  # type: ignore

    @classmethod
    def validate_name(cls, name: str, logger: LoggerType = None) -> bool:
        """Determine if a name is valid for this class."""

        result = cls.name_regex.fullmatch(name) is not None

        if not result and logger is not None:
            logger.warning(
                "Name '%s' didn't match '%s'.", name, cls.name_regex
            )

        return result
