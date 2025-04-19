"""
A module implementing interfaces to include Bootstrap
(https://getbootstrap.com/) in an application.
"""

# third-party
from svgen.element import Element
from svgen.element.html import div

CDN = "cdn.jsdelivr.net"
BOOTSTRAP_VERSION = "5.3.3"
ICONS_VERSION = "1.11.3"


def icon_str(icon: str, classes: list[str] = None) -> str:
    """Get a boostrap icon string."""

    if classes is None:
        classes = []
    classes = ["bi", f"bi-{icon}"] + classes

    return f'<i class="{" ".join(classes)}"></i>'


def bootstrap_icons_url(online: bool, version: str = ICONS_VERSION) -> str:
    """Get a URL for bootstrap-icons CSS."""

    path = "/bootstrap-icons.min.css"
    if online:
        path = f"https://{CDN}/npm/bootstrap-icons@{version}/font" + path
    else:
        path = "/static/css" + path

    return path


def bootsrap_css_url(online: bool, version: str = BOOTSTRAP_VERSION) -> str:
    """Get a URL for bootstrap's CSS."""

    path = "/css/bootstrap.min.css"
    if online:
        path = f"https://{CDN}/npm/bootstrap@{version}/dist" + path
    else:
        path = "/static" + path

    return path


def add_bootstrap_css(element: Element, online: bool) -> None:
    """Add boostrap CSS sources as a child of element."""

    div(
        tag="link",
        rel="stylesheet",
        href=bootstrap_icons_url(online),
        parent=element,
    )

    div(
        tag="link",
        href=bootsrap_css_url(online),
        rel="stylesheet",
        crossorigin="anonymous",
        parent=element,
    )


def bootstrap_js_url(online: bool, version: str = BOOTSTRAP_VERSION) -> str:
    """Get bootstrap's JavaScript URL."""

    path = "/js/bootstrap.bundle.min.js"
    if online:
        path = f"https://cdn.jsdelivr.net/npm/bootstrap@{version}/dist" + path
    else:
        path = "/static" + path

    return path


def add_bootstrap_js(element: Element, online: bool) -> None:
    """Add bootstrap JavaScript as a child of element."""

    div(
        tag="script",
        src=bootstrap_js_url(online),
        crossorigin="anonymous",
        parent=element,
    )
