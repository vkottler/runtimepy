"""
A module implementing markdown-related class mixins.
"""

# built-in
from functools import cache

# third-party
from vcorelib import DEFAULT_ENCODING
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.paths import resource

# internal
from runtimepy import PKG_NAME


@cache
def default_markdown() -> str:
    """Get default markdown contents."""

    path = resource("md", "default.md", package=PKG_NAME, strict=True)
    assert path is not None

    with path.open("r", encoding=DEFAULT_ENCODING) as default:
        result = default.read()
    return result


class MarkdownMixin:
    """A simple markdown class mixin."""

    markdown: str

    def set_markdown(
        self, markdown: str = None, config: _JsonObject = None
    ) -> None:
        """Set markdown for this instance."""

        assert not hasattr(self, "markdown")

        self.markdown: str = (
            markdown  # type: ignore
            or (None if config is None else config.get("markdown"))
            or default_markdown()
        )
