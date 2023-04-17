"""
A module extending capability of the connection arbiter using Python import
machinery.
"""

# built-in
from importlib import import_module as _import_module
from typing import List as _List
from typing import Tuple as _Tuple
from typing import Union as _Union

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

    def set_app(self, module_path: _Union[str, _List[str]]) -> None:
        """
        Attempt to update the application method from the provided string.
        """

        if isinstance(module_path, str):
            module_path = [module_path]

        # Load all application methods.
        apps = []
        for path in module_path:
            module, app = import_str_and_item(path)
            apps.append(getattr(_import_module(module), app))

        self._apps = apps

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
