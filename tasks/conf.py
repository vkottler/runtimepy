"""
A module for project-specific task registration.
"""

# built-in
from pathlib import Path
from typing import Dict

# third-party
from vcorelib.task import Inbox, Outbox, Phony
from vcorelib.task.manager import TaskManager
from vcorelib.task.subprocess.run import SubprocessLogMixin, is_windows


class ArbiterTask(SubprocessLogMixin):
    """A task for running the runtime arbiter."""

    default_requirements = {"vmklib.init", "venv", "python-editable"}

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate ninja configuration files."""

        cwd: Path = args[0]

        configs = cwd.joinpath("local", "arbiter")

        config = configs.joinpath(kwargs.get("config", "test") + ".yaml")

        return await self.exec(
            str(
                inbox["venv"]["venv{python_version}"]["bin"].joinpath(
                    "runtimepy"
                )
            ),
            "arbiter",
            str(config),
        )


def register(
    manager: TaskManager,
    project: str,
    cwd: Path,
    substitutions: Dict[str, str],
) -> bool:
    """Register project tasks to the manager."""

    # Don't run yamllint on Windows because it will fail on newlines.
    manager.register(
        Phony("yaml"),
        [] if is_windows() else ["yaml-lint-local", "yaml-lint-manifest.yaml"],
    )

    manager.register(ArbiterTask("r", cwd))

    del project
    del cwd
    del substitutions

    return True
