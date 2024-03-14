"""
A module implementing some compile_commands.json management interfaces.
"""

# built-in
import asyncio
import json
from pathlib import Path
from typing import NamedTuple

# third-party
from vcorelib import DEFAULT_ENCODING
from vcorelib.asyncio.cli import ProcessResult, run_command
from vcorelib.logging import LoggerMixin, LoggerType
from vcorelib.paths import modified_after, rel


class CompileCommand(NamedTuple):
    """A class implementing a compile-command instance."""

    directory: Path
    args: list[str]
    file: str
    output: str

    @property
    def command(self) -> str:
        """Get the command string for this instance"""
        return " ".join(self.args)

    async def run(self, logger: LoggerType, **kwargs) -> ProcessResult:
        """Run command."""

        # Make sure we switch to the correct directory first?
        await run_command(logger, *self.args, **kwargs)

    def as_dict(self) -> dict[str, str]:
        """Get this instance as a dictionary."""

        return {
            "directory": str(self.directory),
            "command": self.command,
            "file": self.file,
            "output": self.output,
        }


class CompileCommands:
    """A class implementing a 'compile_commands.json' interface."""

    def __init__(self, directory: Path | str) -> None:
        """Initialize this instance."""

        self.directory = str(directory)

        self.commands: list[CompileCommand] = []
        self.by_file: dict[str, CompileCommand] = {}

        # load file if it exists, update current commands
        self.output = Path(self.directory).joinpath("compile_commands.json")

        # Load existing data.
        if self.output.is_file():
            pass

    def write(self) -> None:
        """Write the output file."""

        with self.output.open("w", encoding=DEFAULT_ENCODING) as out_fd:
            json.dump(
                list(x.as_dict() for x in self.commands), out_fd, indent=2
            )

    def add(
        self, source: Path | str, dest: Path | str, cc: str = "emcc"
    ) -> CompileCommand:
        """Add a compile command."""

        directory = Path(self.directory).resolve()

        dest_str = str(rel(dest, directory))
        src_str = str(rel(source, directory))

        # Need to be able to source / specify additional flags. Load from
        # configuration file as well?
        cmd_args = [cc, src_str, "-o", dest_str]

        result = CompileCommand(directory, cmd_args, src_str, dest_str)

        # Update Tracking.
        assert dest_str not in self.by_file, (dest_str, self.by_file[dest_str])
        self.by_file[dest_str] = result
        self.commands.append(result)

        return result


class EmscriptenBuilder(LoggerMixin):
    """A class implementing a simple emscripten-project buliding interface."""

    def __init__(self, logger: LoggerType, root: Path) -> None:
        """Initialize this instances."""

        super().__init__(logger=logger)
        self.root = root
        self.compdb = CompileCommands(self.root)

    async def handle(self, source: Path | str, dest: Path | str) -> None:
        """Add a compile command."""

        command = self.compdb.add(source, dest)

        commands = []

        # Build if necessary.
        if not dest.is_file() or modified_after(dest, [source]):
            commands.append(command.run(self.logger))

        if commands:
            await asyncio.gather(*commands)
            self.compdb.write()
