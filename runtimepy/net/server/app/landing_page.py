"""
A module for developing and testing a top-level landing page idea (#239).
"""

# built-in
from typing import Optional

# third-party
from svgen.element.html import Html

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.http.response import ResponseHeader


def landing_page(
    app: AppInfo,
    document: Html,
    request: RequestHeader,
    response: ResponseHeader,
    request_data: Optional[bytes],
) -> Html:
    """Create a landing page application"""

    # Not currently used.
    del request
    del response
    del request_data

    print(app)

    return document
