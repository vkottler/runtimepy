"""
A module for developing and testing a top-level landing page idea (#239).
"""

# built-in
from typing import Optional

# third-party
from svgen.element import Element
from svgen.element.html import Html, div

# internal
from runtimepy import PKG_NAME
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.http.response import ResponseHeader
from runtimepy.net.server.app.bootstrap import add_bootstrap_js
from runtimepy.net.server.app.bootstrap.tabs import create_app_shell
from runtimepy.net.server.app.css import common_css
from runtimepy.net.server.app.files import append_kind


def landing_page_app(parent: Element) -> None:
    """Compose a landing page."""

    container, _ = create_app_shell(parent, id=PKG_NAME)

    div(text="hello, world!", parent=container, class_str="text-body")


def landing_page(
    app: AppInfo,
    document: Html,
    request: RequestHeader,
    response: ResponseHeader,
    request_data: Optional[bytes],
) -> Html:
    """Create a landing page application"""

    # Not currently used.
    del app
    del request
    del response
    del request_data

    common_css(document)
    landing_page_app(document.body)
    append_kind(document.body, "landing_page")
    add_bootstrap_js(document.body)

    return document
