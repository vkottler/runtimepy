"""
A module implementing application methods for this package's server interface.
"""

# built-in
from contextlib import suppress
from importlib import import_module as _import_module
from typing import Any

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.server import RuntimepyServerConnection
from runtimepy.net.server.app.create import config_param, create_app
from runtimepy.subprocess import spawn_exec
from runtimepy.util import import_str_and_item


async def launch_browser(app: AppInfo) -> None:
    """
    Attempts to launch browser windows/tabs if any 'http_server' server ports
    are configured.
    """

    # Launch browser based on config option.
    if config_param(app, "xdg_open_http", False):

        port: Any
        for port in app.config["root"]["ports"]:  # type: ignore
            if "http_server" in port["name"]:
                # URI parameters.
                hostname = config_param(app, "xdg_host", "localhost")

                # Assemble URI.
                uri = f"http://{hostname}:{port['port']}/"

                # Add a fragment if one was specified.
                fragment = config_param(app, "xdg_fragment", "")
                if fragment:
                    uri += "#" + fragment

                with suppress(FileNotFoundError):
                    await app.stack.enter_async_context(
                        spawn_exec("xdg-open", uri)
                    )


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

    await launch_browser(app)

    return 0
