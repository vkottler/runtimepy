"""
A module implementing interfaces to include Bootstrap
(https://getbootstrap.com/) in an application.
"""

# third-party
from svgen.element import Element

BOOTSTRAP_VERSION = "5.3.3"


def add_bootstrap_css(element: Element) -> None:
    """Add boostrap CSS sources as a child of element."""

    element.children.append(
        Element(
            tag="link",
            href=(
                "https://cdn.jsdelivr.net/npm/bootstrap"
                f"@{BOOTSTRAP_VERSION}/dist/css/bootstrap.min.css"
            ),
            rel="stylesheet",
            crossorigin="anonymous",
        )
    )


def add_bootstrap_js(element: Element) -> None:
    """Add bootstrap JavaScript as a child of element."""

    element.children.append(
        Element(
            tag="script",
            src=(
                "https://cdn.jsdelivr.net/npm/bootstrap"
                f"@{BOOTSTRAP_VERSION}/dist/js/bootstrap.bundle.min.js"
            ),
            crossorigin="anonymous",
            text="/* null */",
        )
    )
