"""
A module extending capability of the connection arbiter using Python import
machinery.
"""

# built-in
from importlib import import_module as _import_module
from typing import Tuple as _Tuple

# internal
from runtimepy.net.arbiter.factory import (
    FactoryConnectionArbiter as _FactoryConnectionArbiter,
)


def import_str_and_item(module_path: str) -> _Tuple[str, str]:
    """
    Treat the last entry in a '.' delimited string as the item to import from
    the module in the string preceding it.
    """

    parts = module_path.split(".")
    assert len(parts) > 1, module_path

    item = parts.pop()
    return ".".join(parts), item


class ImportConnectionArbiter(_FactoryConnectionArbiter):
    """
    A class implementing extensions to the connection arbiter for working with
    arbitrary Python modules.
    """

    def set_app(self, module_path: str) -> None:
        """
        Attempt to update the application method from the provided string.
        """

        module, app = import_str_and_item(module_path)
        self._app = getattr(_import_module(module), app)

    def register_module_factory(
        self, module_path: str, *namespaces: str, **kwargs
    ) -> bool:
        """Attempt to register a factory class based on its module path."""

        module, factory_class = import_str_and_item(module_path)

        return self.register_factory(
            # We need to call the factory class to create an instance.
            getattr(_import_module(module), factory_class)(**kwargs),
            *namespaces,
        )
