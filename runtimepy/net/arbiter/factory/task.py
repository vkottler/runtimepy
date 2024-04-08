"""
A module implementing task-factory registration.
"""

# third-party
from vcorelib.names import obj_class_to_snake

# internal
from runtimepy.net.arbiter.base import (
    BaseConnectionArbiter as _BaseConnectionArbiter,
)
from runtimepy.net.arbiter.task import ArbiterTask as _ArbiterTask
from runtimepy.net.arbiter.task import TaskFactory as _TaskFactory

Factory = _TaskFactory[_ArbiterTask]


class TaskConnectionArbiter(_BaseConnectionArbiter):
    """A class for managing task factories."""

    def _init(self) -> None:
        """Additional initialization tasks."""

        super()._init()
        self._task_factories: dict[str, Factory] = {}
        self._task_names: dict[Factory, list[str]] = {}

    def factory_task(
        self, factory: str, name: str, period_s: float = None, **kwargs
    ) -> bool:
        """
        Register a periodic task from one of the registered task factories.
        """

        result = False

        if factory in self._task_factories:
            result = self.task_manager.register(
                self._task_factories[factory].kind(name, **kwargs),
                period_s=period_s,
            )

        return result

    def register_task_factory(
        self, factory: Factory, *namespaces: str
    ) -> bool:
        """Attempt to register a periodic task factory."""

        result = False

        assert isinstance(factory, _TaskFactory), factory

        name = factory.__class__.__name__
        snake_name = obj_class_to_snake(factory)

        if (
            name not in self._task_factories
            and snake_name not in self._task_factories
        ):
            self._task_factories[name] = factory
            self._task_factories[snake_name] = factory
            self._task_names[factory] = [*namespaces]

            result = True
            self.logger.debug(
                "Registered '%s' (%s) task factory.", name, snake_name
            )

        return result
