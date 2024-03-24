"""
A module implementing application methods for this package's server interface.
"""

# built-in
from importlib import import_module as _import_module

# internal
from runtimepy.net.arbiter.imports import import_str_and_item
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.server import RuntimepyServerConnection
from runtimepy.net.server.app.create import config_param, create_app


async def setup(app: AppInfo) -> int:
    """Perform server application setup steps."""

    # Set default application.
    module, method = import_str_and_item(
        config_param(
            app,
            "html_method",
            "runtimepy.net.server.app.env.channel_environments",
        )
    )
    RuntimepyServerConnection.default_app = create_app(
        app, getattr(_import_module(module), method)
    )

    return 0
