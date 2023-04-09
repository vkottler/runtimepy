"""
A module extending capability of the connection arbiter using Python import
machinery.
"""

# built-in
from importlib import import_module as _import_module

# internal
from runtimepy.net.arbiter.factory import (
    FactoryConnectionArbiter as _FactoryConnectionArbiter,
)


class ImportConnectionArbiter(_FactoryConnectionArbiter):
    """
    A class implementing extensions to the connection arbiter for working with
    arbitrary Python modules.
    """

    def register_module_factory(
        self, module_path: str, *namespaces: str, **kwargs
    ) -> bool:
        """Attempt to register a factory class based on its module path."""

        parts = module_path.split(".")
        assert len(parts) > 1

        factory_class = parts.pop()

        return self.register_factory(
            # We need to call the factory class to create an instance.
            getattr(_import_module(".".join(parts)), factory_class)(**kwargs),
            *namespaces,
        )
