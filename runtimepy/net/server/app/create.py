"""
A module implementing a simple application harnessing interface.
"""

# built-in
from typing import Callable, Optional, TypeVar

# third-party
from svgen.element.html import Html
from vcorelib.logging import LoggerMixin

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.html.bootstrap.tabs import TabbedContent
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.http.response import ResponseHeader
from runtimepy.net.server.app.base import WebApplication
from runtimepy.net.server.html import HtmlApp

DOCUMENTS: dict[str, Html] = {}
T = TypeVar("T")


def config_param(
    app: AppInfo, key: str, default: T, strict: bool = False
) -> T:
    """Attempt to get a configuration parameter."""
    return app.config_param(key, default, strict=strict)


HtmlAppComposer = Callable[
    [AppInfo, Html, RequestHeader, ResponseHeader, Optional[bytes]], Html
]


def create_cacheable_app(app: AppInfo, compose: HtmlAppComposer) -> HtmlApp:
    """
    Create a web application-serving method capable of automatically caching
    the originally composed document.
    """

    async def cached_app(
        document: Html,
        request: RequestHeader,
        response: ResponseHeader,
        request_data: Optional[bytes],
    ) -> Html:
        """A simple 'Hello, world!' application."""

        with LoggerMixin(logger=app.logger).log_time(
            "Composing HTML document"
        ):
            populate = True

            compose_name = compose.__name__

            # Use the already-rendered document.
            if config_param(app, "caching", True):
                if compose_name in DOCUMENTS:
                    document = DOCUMENTS[compose_name]
                    populate = False

            if populate:
                # Create the application.
                document = compose(
                    app, document, request, response, request_data
                )
                DOCUMENTS[compose_name] = document

        return document

    return cached_app


def create_app(
    app: AppInfo, compose: Callable[[AppInfo, TabbedContent], None]
) -> HtmlApp:
    """Create a web-application handler."""

    def main(
        app: AppInfo,
        document: Html,
        request: RequestHeader,
        response: ResponseHeader,
        request_data: Optional[bytes],
    ) -> Html:
        """Main package web application."""

        # Not currently used.
        del request
        del response
        del request_data

        WebApplication(app).populate(document, lambda tabs: compose(app, tabs))

        return document

    return create_cacheable_app(app, main)
