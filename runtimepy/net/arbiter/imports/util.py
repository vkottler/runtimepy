"""
Utility interfaces for arbiter runtime-import mechanisms.
"""

# built-in
from importlib import import_module as _import_module

# internal
from runtimepy.net.arbiter.config.codec import ConfigApps
from runtimepy.net.arbiter.info import ArbiterApps
from runtimepy.util import import_str_and_item


def get_apps(
    module_path: ConfigApps, wait_for_stop: bool = False
) -> ArbiterApps:
    """
    Attempt to update the application method from the provided string.
    """

    if module_path is None:
        module_path = []
    elif isinstance(module_path, str):
        module_path = [module_path]

    if wait_for_stop:
        module_path.append("runtimepy.net.apps.wait_for_stop")

    # Load all application methods.
    apps = []
    for paths in module_path:
        if not isinstance(paths, list):
            paths = [paths]  # type: ignore

        methods = []
        for path in paths:
            module, app = import_str_and_item(path)
            methods.append(getattr(_import_module(module), app))

        apps.append(methods)

    return apps
