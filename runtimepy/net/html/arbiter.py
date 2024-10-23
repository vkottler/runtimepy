"""
A module implementing connection-arbiter related utilities.
"""

# internal
from runtimepy.net.arbiter.config import ConfigObject


def web_app_paths(config: ConfigObject) -> None:
    """
    Register boilerplate path handling for additional application-serving URIs.
    """

    config.setdefault("config", {})
    redirects = config["config"].setdefault("http_redirects", {})
    app_paths = config["config"].setdefault("http_app_paths", [])

    for prefix in config["config"].get("http_app_prefixes", []):
        if not prefix.startswith("/"):
            prefix = "/" + prefix

        assert not prefix.endswith("/"), prefix

        # Add re-directs.
        index_path = f"{prefix}/index.html"
        app_path = f"{prefix}/app.html"
        redirects.setdefault(prefix, index_path)
        redirects.setdefault(index_path, app_path)

        # Add app path.
        if app_path not in app_paths:
            app_paths.append(app_path)
