"""
A module implementing CSS-related interfaces.
"""

# third-party
from svgen.element.html import Html

# internal
from runtimepy.net.server.app.bootstrap import add_bootstrap_css
from runtimepy.net.server.app.files import append_kind


def common_css(document: Html) -> None:
    """Add common CSS to an HTML document."""

    append_kind(document.head, "font", kind="css", tag="style")
    add_bootstrap_css(document.head)
    append_kind(
        document.head, "main", "bootstrap_extra", kind="css", tag="style"
    )
