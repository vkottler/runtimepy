"""
A module implementing UI command processing.
"""

# built-in
from collections import UserDict
from contextlib import ExitStack, contextmanager
import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Iterator, Optional, cast

# third-party
from vcorelib import DEFAULT_ENCODING
from vcorelib.io import ARBITER, JsonObject
from vcorelib.logging import DEFAULT_TIME_FORMAT, LoggerMixin
from vcorelib.math import default_time_ns, nano_str
from vcorelib.names import name_search

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.channel.environment.base import FieldOrChannel
from runtimepy.channel.environment.command.processor import (
    ChannelCommandProcessor,
    CommandHook,
    EnvironmentMap,
)
from runtimepy.channel.registry import ParsedEvent
from runtimepy.mapping import DEFAULT_PATTERN

# Declared so we re-export FieldOrChannel after moving where it's declared.
__all__ = [
    "CommandHook",
    "FieldOrChannel",
    "EnvironmentMap",
    "GLOBAL",
    "ENVIRONMENTS",
    "clear_env",
    "register_env",
    "GlobalEnvironment",
]
EVENT_OUT = "event_stream.bin"


class GlobalEnvironment(UserDict[str, ChannelCommandProcessor], LoggerMixin):
    """
    A class implementing a container for channel environments available
    globally at runtime.
    """

    def __init__(self, root: Path = None) -> None:
        """Initialize this instance."""

        super().__init__()
        LoggerMixin.__init__(self)
        self.root: Optional[Path] = root

    @staticmethod
    def from_root(root: Path) -> "GlobalEnvironment":
        """Load a global environment from a directory."""

        result = GlobalEnvironment(root=root)

        # Load metadata.
        data = ARBITER.decode(
            GlobalEnvironment.meta_path(root), require_success=True
        ).data

        # Log path and duration.
        duration_ns = cast(int, data["end_ns"]) - cast(int, data["start_ns"])
        result.logger.info(
            "Loading environment at '%s' that executed for %ss.",
            root,
            nano_str(duration_ns, is_time=True),
        )

        # Log channel information.
        tlm: dict[str, list[str]] = data["event_telemetry"]  # type: ignore
        for env_name, channels in tlm.items():
            result.logger.info("%s: %s.", env_name, ", ".join(channels))
            result[env_name] = ChannelCommandProcessor(
                ChannelEnvironment.load_directory(
                    result.valid_root.joinpath(env_name)
                ),
                logging.getLogger(env_name),
            )

        return result

    @staticmethod
    @contextmanager
    def temporary() -> Iterator["GlobalEnvironment"]:
        """Create a temporary global environment."""
        with TemporaryDirectory() as tmpdir:
            yield GlobalEnvironment(root=Path(tmpdir))

    @contextmanager
    def file_event_stream(
        self,
        env: str,
        pattern: str = DEFAULT_PATTERN,
        path: str = EVENT_OUT,
        exact: bool = False,
    ) -> Iterator[list[str]]:
        """Enable event streaming to a file for an environment by name."""

        with self.export(env).joinpath(path).open("wb") as path_fd:
            with self[env].env.channels.registered(
                path_fd, pattern=pattern, exact=exact
            ) as chans:
                yield chans

    def read_event_stream(
        self, env: str, path: str = EVENT_OUT
    ) -> Iterator[ParsedEvent]:
        """Reade events from a specific environment."""

        with self.valid_root.joinpath(env, path).open("rb") as path_fd:
            yield from self[env].env.parse_event_stream(path_fd)

    def export(self, env: str) -> Path:
        """Export an environment to a sub-directory of the root directory."""

        out = self.valid_root.joinpath(env)
        out.mkdir(exist_ok=True, parents=True)

        # Export data.
        self[env].env.export_directory(out)

        return out

    @property
    def valid_root(self) -> Path:
        """Get the validated root directory."""
        assert self.root is not None, "No output directory set!"
        return self.root

    @staticmethod
    def meta_path(root: Path) -> Path:
        """Get the path to the metadata file."""
        return root.joinpath("meta.json")

    def write_meta(self, data: JsonObject) -> None:
        """Write metadata to the output directory."""
        ARBITER.encode(GlobalEnvironment.meta_path(self.valid_root), data)

    @contextmanager
    def log_file(self, path: str = "log.txt") -> Iterator[logging.FileHandler]:
        """Register a logging file handler as a managed context."""

        handler = logging.FileHandler(
            str(self.valid_root.joinpath(path)), encoding=DEFAULT_ENCODING
        )
        handler.setFormatter(logging.Formatter(DEFAULT_TIME_FORMAT))
        root = logging.getLogger()
        root.addHandler(handler)

        try:
            yield handler
        finally:
            handler.close()
            root.removeHandler(handler)

    @contextmanager
    def event_telemetry_output(
        self,
        env_pattern: str = DEFAULT_PATTERN,
        env_exact: bool = False,
        channel_pattern: str = DEFAULT_PATTERN,
        channel_exact: bool = False,
        event_path: str = EVENT_OUT,
        text_log: bool = True,
    ) -> Iterator[list[tuple[str, list[str]]]]:
        """Register file-output streams for environments based on a pattern."""

        metadata: JsonObject = {
            "root": str(self.valid_root),
            "env_pattern": env_pattern,
            "env_exact": env_exact,
            "channel_pattern": channel_pattern,
            "channel_exact": channel_exact,
            "event_path": event_path,
            "text_log": text_log,
        }

        with ExitStack() as stack:
            if text_log:
                stack.enter_context(self.log_file())

            name_channels = []
            for name in name_search(self, env_pattern, exact=env_exact):
                # Set up event telemetry.
                chans = stack.enter_context(
                    self.file_event_stream(
                        name,
                        pattern=channel_pattern,
                        path=event_path,
                        exact=channel_exact,
                    )
                )
                name_channels.append((name, chans))

                if text_log:
                    self.logger.info(
                        "Environment '%s' channel event telemetry for: %s.",
                        name,
                        ", ".join(chans),
                    )

            metadata["event_telemetry"] = dict(name_channels)  # type: ignore
            with self.log_time(
                "Event-telemetry logged context", reminder=True
            ):
                metadata["start_ns"] = default_time_ns()
                yield name_channels
                metadata["end_ns"] = default_time_ns()

        self.write_meta(metadata)

    def clear(self) -> None:
        """Log environments that get cleared when clearing."""

        envs = list(self)
        if envs:
            super().clear()
            self.logger.info(
                "Cleared the following environments: %s.", ", ".join(envs)
            )

    def register(self, name: str, env: ChannelCommandProcessor) -> None:
        """Register an environment."""

        assert (
            name not in self or self[name] is env
        ), f"Can't register environment '{name}'!"

        if name not in self:
            self[name] = env
            self.logger.debug("Registered channel environment '%s'.", name)


GLOBAL = GlobalEnvironment()
ENVIRONMENTS = GLOBAL


def clear_env() -> None:
    """Reset the global environment mapping."""
    GLOBAL.clear()


def env_json_data() -> dict[str, Any]:
    """Get JSON data for each environment."""
    return {key: cmd.env.export_json for key, cmd in GLOBAL.items()}


def register_env(name: str, env: ChannelCommandProcessor) -> None:
    """Register a channel environment globally."""
    GLOBAL.register(name, env)
