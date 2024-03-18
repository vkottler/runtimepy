"""
A module implementing application methods for this package's server interface.
"""

# built-in
from importlib import import_module as _import_module

# internal
from runtimepy.net.arbiter.imports import import_str_and_item
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.server import RuntimepyServerConnection
from runtimepy.net.server.app.bootstrap.tabs import TabbedContent
from runtimepy.net.server.app.create import config_param, create_app
from runtimepy.net.server.app.tab import Tab


def sample(app: AppInfo, tabs: TabbedContent) -> None:
    """Populate application elements."""

    # Add dev tab.
    Tab("example", app, tabs, source="dev").entry()

    for idx in range(10):
        Tab(f"test{idx}", app, tabs, source="example").entry()


async def setup(app: AppInfo) -> int:
    """Perform server application setup steps."""

    # Set default application.
    module, method = import_str_and_item(
        config_param(app, "html_method", "runtimepy.net.server.app.sample")
    )
    RuntimepyServerConnection.default_app = create_app(
        app, getattr(_import_module(module), method)
    )

    return 0
