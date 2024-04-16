"""
A module implementing interfaces to the pyodide project.
"""

# third-party
from svgen.element import Element
from svgen.element.html import div

PYODIDE_VERSION = "0.25.0"


def add_pyodide_js(element: Element) -> Element:
    """Add bootstrap JavaScript as a child of element."""

    return div(
        tag="script",
        src=(
            "https://cdn.jsdelivr.net/pyodide/"
            f"v{PYODIDE_VERSION}/full/pyodide.js"
        ),
        parent=element,
    )
