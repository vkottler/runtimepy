"""
A module extending capability of the connection arbiter using Python import
machinery.
"""

# built-in
from importlib import import_module as _import_module

# third-party
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.names import import_str_and_item, to_snake

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
from runtimepy.net.arbiter.info import RuntimeStruct as _RuntimeStruct
from runtimepy.net.arbiter.task import TaskFactory as _TaskFactory
from runtimepy.subprocess.peer import RuntimepyPeer as _RuntimepyPeer


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

        self._struct_factories: dict[str, type[_RuntimeStruct]] = {}
        self._struct_names: dict[type[_RuntimeStruct], list[str]] = {}

        self._peer_factories: dict[str, type[_RuntimepyPeer]] = {}
        self._peer_names: dict[type[_RuntimepyPeer], list[str]] = {}

    def register_peer_factory(
        self, factory: type[_RuntimepyPeer], *namespaces: str
    ) -> bool:
        """Attempt to register a subprocess peer factory."""

        result = False

        name = factory.__name__
        snake_name = to_snake(name)

        if (
            name not in self._peer_factories
            and snake_name not in self._peer_factories
        ):
            self._peer_factories[name] = factory
            self._peer_factories[snake_name] = factory
            self._peer_names[factory] = [*namespaces]

            result = True
            self.logger.debug(
                "Registered '%s' (%s) subprocess peer factory.",
                name,
                snake_name,
            )

        return result

    def register_struct_factory(
        self, factory: type[_RuntimeStruct], *namespaces: str
    ) -> bool:
        """Attempt to register a struct factory."""

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

    def factory_struct(
        self, factory: str, name: str, config: _JsonObject
    ) -> bool:
        """Register a runtime structure from factory and name."""

        result = False

        if factory in self._struct_factories and name not in self._structs:
            self._structs[name] = self._struct_factories[factory](name, config)
            result = True

        return result

    def factory_process(
        self, factory: str, name: str, top_level: _JsonObject
    ) -> bool:
        """Register a runtime process."""

        result = False

        if factory in self._peer_factories and name not in self._peers:
            self._peers[name] = (
                self._peer_factories[factory],
                name,
                top_level.get("config", {}),  # type: ignore
                str(top_level["program"]),
                top_level.get("markdown"),
            )
            result = True

        return result

    def register_module_factory(
        self, module_path: str, *namespaces: str, **kwargs
    ) -> bool:
        """Attempt to register a factory class based on its module path."""

        module, factory_class = import_str_and_item(module_path)

        raw_import = getattr(_import_module(module), factory_class)

        result = False

        # Handle factories that don't need factory-class proxying.
        if isinstance(raw_import, type):
            if issubclass(raw_import, _RuntimeStruct):
                result = self.register_struct_factory(raw_import, *namespaces)
            elif issubclass(raw_import, _RuntimepyPeer):
                result = self.register_peer_factory(raw_import, *namespaces)

        if not result:
            # We need to call the factory class to create an instance.
            inst = raw_import(**kwargs)

            # Determine what kind of factory to register.
            result = False
            if isinstance(inst, _ConnectionFactory):
                result = self.register_connection_factory(inst, *namespaces)
            elif isinstance(inst, _TaskFactory):
                result = self.register_task_factory(inst, *namespaces)

        return result
