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


def add_bootstrap_css(element: Element) -> None:
    """Add boostrap CSS sources as a child of element."""

    div(
        tag="link",
        rel="stylesheet",
        href=(
            f"https://{CDN}/npm/"
            f"bootstrap-icons@{ICONS_VERSION}/font/bootstrap-icons.min.css"
        ),
        parent=element,
    )

    div(
        tag="link",
        href=(
            f"https://{CDN}/npm/bootstrap"
            f"@{BOOTSTRAP_VERSION}/dist/css/bootstrap.min.css"
        ),
        rel="stylesheet",
        crossorigin="anonymous",
        parent=element,
    )


def add_bootstrap_js(element: Element) -> None:
    """Add bootstrap JavaScript as a child of element."""

    div(
        tag="script",
        src=(
            "https://cdn.jsdelivr.net/npm/bootstrap"
            f"@{BOOTSTRAP_VERSION}/dist/js/bootstrap.bundle.min.js"
        ),
        crossorigin="anonymous",
        parent=element,
    )
