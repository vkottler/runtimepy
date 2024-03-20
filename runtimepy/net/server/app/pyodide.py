"""
A module implementing interfaces to the pyodide project.
"""

# third-party
from svgen.element import Element

PYODIDE_VERSION = "0.25.0"


def add_pyodide_js(element: Element) -> Element:
    """Add bootstrap JavaScript as a child of element."""

    elem = Element(
        tag="script",
        src=(
            "https://cdn.jsdelivr.net/pyodide/"
            f"v{PYODIDE_VERSION}/full/pyodide.js"
        ),
        allow_no_end_tag=False,
    )
    element.children.append(elem)
    return elem
