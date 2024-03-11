"""
A module implementing a simple application harnessing interface.
"""

# built-in
from typing import Callable, Optional, TypeVar

# third-party
from svgen.element.html import Html

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.http.response import ResponseHeader
from runtimepy.net.server.app.base import WebApplication
from runtimepy.net.server.app.bootstrap.tabs import TabbedContent
from runtimepy.net.server.html import HtmlApp

DOCUMENT = None
T = TypeVar("T")


def config_param(app: AppInfo, key: str, default: T) -> T:
    """Attempt to get a configuration parameter."""

    config: dict[str, T] = app.config["root"].setdefault(  # type: ignore
        "config",
        {},
    )
    return config.get(key, default)


def create_app(
    app: AppInfo, compose: Callable[[AppInfo, TabbedContent], None]
) -> HtmlApp:
    """Create a web-application handler."""

    def _compose(tabs: TabbedContent) -> None:
        """A simple compose wrapper."""
        compose(app, tabs)

    async def main(
        document: Html,
        request: RequestHeader,
        response: ResponseHeader,
        request_data: Optional[bytes],
    ) -> Html:
        """A simple 'Hello, world!' application."""

        # Use the already-rendered document.
        if config_param(app, "caching", True):
            global DOCUMENT  # pylint: disable=global-statement
            if DOCUMENT is not None:
                return DOCUMENT

        # Not currently used.
        del request
        del response
        del request_data

        # Create the application.
        WebApplication(app).populate(document, _compose)

        DOCUMENT = document
        return document

    return main
