"""
A module extending capability of the connection arbiter using Python import
machinery.
"""

# built-in
from importlib import import_module as _import_module
from typing import Dict as _Dict
from typing import List as _List
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Type as _Type
from typing import Union as _Union

# third-party
from vcorelib.names import to_snake

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
from runtimepy.net.arbiter.struct import RuntimeStruct as _RuntimeStruct
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

    def _init(self) -> None:
        """Additional initialization tasks."""

        super()._init()
        self._struct_factories: _Dict[str, _Type[_RuntimeStruct]] = {}
        self._struct_names: _Dict[_Type[_RuntimeStruct], _List[str]] = {}

    def set_app(
        self,
        module_path: _Optional[_Union[str, _List[str]]],
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

    def register_struct_factory(
        self, factory: _Type[_RuntimeStruct], *namespaces: str
    ) -> bool:
        """Attempt to register a periodic task factory."""

        result = False

        name = factory.__name__
        snake_name = to_snake(name)

        if (
            name not in self._struct_factories
            and snake_name not in self._struct_factories
        ):
            self._struct_factories[name] = factory
            self._struct_factories[snake_name] = factory
            self._struct_names[factory] = [*namespaces]

            result = True
            self.logger.debug(
                "Registered '%s' (%s) struct factory.", name, snake_name
            )

        return result

    def factory_struct(self, factory: str, name: str) -> bool:
        """Register a runtime structure from factory and name."""

        result = False

        if factory in self._struct_factories and name not in self._structs:
            self._structs[name] = self._struct_factories[factory](name)
            result = True

        return result

    def register_module_factory(
        self, module_path: str, *namespaces: str, **kwargs
    ) -> bool:
        """Attempt to register a factory class based on its module path."""

        module, factory_class = import_str_and_item(module_path)

        raw_import = getattr(_import_module(module), factory_class)

        # Handle factories that don't need factory-class proxying.
        if (
            isinstance(raw_import, type)
            and _RuntimeStruct in raw_import.__bases__
        ):
            result = self.register_struct_factory(raw_import, *namespaces)

        else:
            # We need to call the factory class to create an instance.
            inst = raw_import(**kwargs)

            # Determine what kind of factory to register.
            result = False
            if isinstance(inst, _ConnectionFactory):
                result = self.register_connection_factory(inst, *namespaces)
            elif isinstance(inst, _TaskFactory):
                result = self.register_task_factory(inst, *namespaces)

        return result
