"""
A module implementing a web application base.
"""

# built-in
from typing import Callable

# third-party
from svgen.element import Element
from svgen.element.html import Html

# internal
from runtimepy import PKG_NAME
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.server.app.bootstrap import (
    add_bootstrap_css,
    add_bootstrap_js,
)
from runtimepy.net.server.app.bootstrap.tabs import TabbedContent
from runtimepy.net.server.app.elements import div
from runtimepy.net.server.app.files import append_kind

TabPopulater = Callable[[TabbedContent], None]

JQUERY_VERSION = "3.7.1"
JQUERY_UI = "1.13.2"


def add_jquery_js(parent: Element, version: str = "3.7.1") -> None:
    """Add jquery to the document."""

    div(
        tag="script",
        parent=parent,
        src=f"https://code.jquery.com/jquery-{version}.js",
        crossorigin="anonymous",
        integrity="sha256-eKhayi8LEQwp4NKxN+CfCh+3qOVUtJn3QNZ0TciWLP4=",
        allow_no_end_tag=False,
    )

    div(
        tag="script",
        parent=parent,
        crossorigin="anonymous",
        src=f"https://code.jquery.com/ui/{JQUERY_UI}/jquery-ui.min.js",
        integrity="sha256-lSjKY0/srUM9BE3dPm+c4fBo1dky2v27Gdjm2uoZaL0=",
        allow_no_end_tag=False,
    )


class WebApplication:
    """A simple web-application interface."""

    worker_classes = ["JsonConnection", "DataConnection", "PlotManager"]
    ui_classes = [
        "WindowHashManager",
        "WorkerInterface",
        "Plot",
        "TabInterface",
        "TabFilter",
        "App",
    ]

    def __init__(self, app: AppInfo) -> None:
        """Initialize this instance."""
        self.app = app

    def populate(self, document: Html, app: TabPopulater) -> None:
        """Populate the body element with the application."""

        # Third-party dependencies.
        add_bootstrap_css(document.head)
        div(
            tag="link",
            rel="stylesheet",
            href=(
                f"https://code.jquery.com/ui/{JQUERY_UI}"
                "/themes/base/jquery-ui.css"
            ),
            parent=document.head,
        )

        # Internal CSS.
        append_kind(
            document.head, "main", "bootstrap_extra", kind="css", tag="style"
        )

        # Worker code.
        append_kind(
            document.body,
            *self.worker_classes,
            subdir="classes",
            worker=True,
        )
        append_kind(document.body, "worker", worker=True)

        # Set up worker.
        append_kind(document.body, "init")
        append_kind(document.body, *self.ui_classes, subdir="classes")

        # Populate applicaton elements.
        app(TabbedContent(PKG_NAME, document.body))

        # Main-thread code.
        append_kind(document.body, "util", "main")

        # Third-party dependencies.
        add_bootstrap_js(document.body)
        add_jquery_js(document.body)
