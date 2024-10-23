"""
A module implementing application methods for this package's server interface.
"""

# built-in
from contextlib import suppress
from importlib import import_module as _import_module
from typing import Any

# third-party
from vcorelib.names import import_str_and_item

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.server import RuntimepyServerConnection
from runtimepy.net.server.app.create import (
    config_param,
    create_app,
    create_cacheable_app,
)
from runtimepy.net.server.app.landing_page import landing_page
from runtimepy.subprocess import spawn_exec


async def launch_browser(app: AppInfo) -> None:
    """
    Attempts to launch browser windows/tabs if any 'http_server' server ports
    are configured.
    """

    # Launch browser based on config option.
    for prefix in ["http", "https"]:
        if config_param(app, f"xdg_open_{prefix}", False):

            port: Any
            for port in app.config["root"]["ports"]:  # type: ignore
                if f"{prefix}_server" in port["name"]:
                    # URI parameters.
                    hostname = config_param(app, "xdg_host", "localhost")

                    # Assemble URI.
                    uri = f"{prefix}://{hostname}:{port['port']}/"

                    # Add a fragment if one was specified.
                    fragment = config_param(app, "xdg_fragment", "")
                    if fragment:
                        uri += "#" + fragment

                    with suppress(FileNotFoundError):
                        await app.stack.enter_async_context(
                            spawn_exec("xdg-open", uri)
                        )


# Could add an interface for adding multiple applications.
APPS = {"landing_page": landing_page}


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

    # Default application (environment tabs).
    html_app = create_app(app, getattr(_import_module(module), method))
    target: str
    for target in app.config_param("http_app_paths", []):
        RuntimepyServerConnection.apps[target] = html_app

    # Register redirects.
    redirects: dict[str, str] = app.config_param("http_redirects", {})
    for key, val in redirects.items():
        RuntimepyServerConnection.add_redirect_path(val, key)

    # Register custom applications.
    for key, app_method in APPS.items():
        app_cfg: dict[str, Any] = app.config_param(key, {})
        paths = app_cfg.get("paths", [])
        if paths:
            # Only create a handler if paths are configured to serve the app.
            created = create_cacheable_app(app, app_method)
            for path in paths:
                RuntimepyServerConnection.apps[path] = created

    await launch_browser(app)

    return 0
