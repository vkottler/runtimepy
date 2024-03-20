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
from runtimepy.net.server.app.env import ChannelEnvironmentTab
from runtimepy.net.server.app.placeholder import dummy_tabs, under_construction


async def setup(app: AppInfo) -> int:
    """Perform server application setup steps."""

    # Set default application.
    module, method = import_str_and_item(
        config_param(
            app, "html_method", "runtimepy.net.server.app.channel_environments"
        )
    )
    RuntimepyServerConnection.default_app = create_app(
        app, getattr(_import_module(module), method)
    )

    return 0


def channel_environments(app: AppInfo, tabs: TabbedContent) -> None:
    """Populate application elements."""

    # Connection tabs.
    for name, conn in app.connections.items():
        ChannelEnvironmentTab(
            name, conn.command, app, tabs, icon="ethernet"
        ).entry()

    # Task tabs.
    for name, task in app.tasks.items():
        ChannelEnvironmentTab(
            name, task.command, app, tabs, icon="arrow-repeat"
        ).entry()

    # Add a bunch of dummy tabs.
    dummy_tabs(5, app, tabs)

    under_construction(tabs.tabs)
