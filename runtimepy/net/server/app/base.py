"""
A module implementing a web application base.
"""

# built-in
from typing import Callable

# third-party
from svgen.element.html import Html

# internal
from runtimepy import PKG_NAME
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.html import append_kind, common_css
from runtimepy.net.html.bootstrap import add_bootstrap_js
from runtimepy.net.html.bootstrap.tabs import TabbedContent

TabPopulater = Callable[[TabbedContent], None]


class WebApplication:
    """A simple web-application interface."""

    worker_classes = [
        "JsonConnection",
        "DataConnection",
        "PointBuffer",
        "PointManager",
        "UnitSystem",
        "OverlayManager",
        "PlotDrawer",
        "PlotManager",
    ]
    ui_classes = [
        "WindowHashManager",
        "WorkerInterface",
        "PlotModalManager",
        "Plot",
        "ChannelTable",
        "TabInterface",
        "TabFilter",
        "App",
    ]

    def __init__(self, app: AppInfo) -> None:
        """Initialize this instance."""
        self.app = app

    def populate(self, document: Html, app: TabPopulater) -> None:
        """Populate the body element with the application."""

        # CSS.
        common_css(document)

        # Worker code.
        append_kind(
            document.body,
            *self.worker_classes,
            subdir="classes",
            worker=True,
        )
        append_kind(document.body, "worker", worker=True)

        # Set up worker.
        append_kind(document.body, "init", "events")
        append_kind(document.body, *self.ui_classes, subdir="classes")

        # Populate applicaton elements.
        app(TabbedContent(PKG_NAME, document.body))

        # Main-thread code.
        append_kind(document.body, "util", "main")

        # Third-party dependencies.
        add_bootstrap_js(document.body)
