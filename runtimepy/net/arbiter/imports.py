"""
A module extending capability of the connection arbiter using Python import
machinery.
"""

# built-in
from importlib import import_module as _import_module
from typing import List as _List
from typing import Optional
from typing import Tuple as _Tuple
from typing import Union as _Union

# internal
from runtimepy.net.arbiter.factory import (
    ConnectionFactory as _ConnectionFactory,
)
from runtimepy.net.arbiter.factory import (
    FactoryConnectionArbiter as _FactoryConnectionArbiter,
)
from runtimepy.net.arbiter.factory.task import (
    TaskConnectionArbiter as _TaskConnectionArbiter,
)
from runtimepy.net.arbiter.task import TaskFactory as _TaskFactory


def import_str_and_item(module_path: str) -> _Tuple[str, str]:
    """
    Treat the last entry in a '.' delimited string as the item to import from
    the module in the string preceding it.
    """

    parts = module_path.split(".")
    assert len(parts) > 1, module_path

    item = parts.pop()
    return ".".join(parts), item


class ImportConnectionArbiter(
    _FactoryConnectionArbiter, _TaskConnectionArbiter
):
    """
    A class implementing extensions to the connection arbiter for working with
    arbitrary Python modules.
    """

    def set_app(
        self,
        module_path: Optional[_Union[str, _List[str]]],
        wait_for_stop: bool = False,
    ) -> None:
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

        if apps:
            self._apps = apps

    def register_module_factory(
        self, module_path: str, *namespaces: str, **kwargs
    ) -> bool:
        """Attempt to register a factory class based on its module path."""

        module, factory_class = import_str_and_item(module_path)

        # We need to call the factory class to create an instance.
        inst = getattr(_import_module(module), factory_class)(**kwargs)

        # Determine what kind of factory to register.
        result = False
        if isinstance(inst, _ConnectionFactory):
            result = self.register_connection_factory(inst, *namespaces)
        elif isinstance(inst, _TaskFactory):
            result = self.register_task_factory(inst, *namespaces)

        return result
