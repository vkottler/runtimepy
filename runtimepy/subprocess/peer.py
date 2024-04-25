"""
A module implementing a runtimepy peer interface.
"""

# built-in
import asyncio
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from sys import executable
from typing import AsyncIterator, Type, TypeVar

# third-party
from vcorelib.io import ARBITER, DEFAULT_INCLUDES_KEY
from vcorelib.io.file_writer import IndentedFileWriter
from vcorelib.io.types import JsonObject
from vcorelib.paths.context import tempfile

# internal
from runtimepy.subprocess import spawn_exec, spawn_shell
from runtimepy.subprocess.interface import RuntimepyPeerInterface
from runtimepy.subprocess.protocol import RuntimepySubprocessProtocol
from runtimepy.util import import_str_and_item

T = TypeVar("T", bound="RuntimepyPeer")


class RuntimepyPeer(RuntimepyPeerInterface):
    """A class implementing an interface for messaging peer subprocesses."""

    def __init__(
        self,
        protocol: RuntimepySubprocessProtocol,
        name: str,
        config: JsonObject,
    ) -> None:
        """Initialize this instance."""

        super().__init__(name, config)
        self.protocol = protocol

        # Offset message identifiers.
        self.curr_id.curr_id += 1

    async def _poll(self) -> None:
        """Poll input queues."""

        keep_going = True
        task = None

        while keep_going:
            try:
                if task is None:
                    task = asyncio.create_task(self.process_command_queue())
                elif task.done():
                    task = None

                keep_going = await self.service_queues()

                if keep_going:
                    await asyncio.sleep(self.poll_period_s)

            except asyncio.CancelledError:
                keep_going = False

    @asynccontextmanager
    async def _context(self: T) -> AsyncIterator[T]:
        """A managed context for the peer."""

        # Register task that will poll queues.
        task = asyncio.create_task(self._poll())

        try:
            with suppress(AssertionError):
                if await self.loopback():
                    await self.wait_json({"meta": self.meta})
                    await self.share_environment()

            yield self
        finally:
            task.cancel()
            await task

    @classmethod
    @asynccontextmanager
    async def shell(
        cls: Type[T], name: str, config: JsonObject, cmd: str
    ) -> AsyncIterator[T]:
        """Create an instance from a shell command."""

        async with spawn_shell(
            cmd, stdout=asyncio.Queue(), stderr=asyncio.Queue()
        ) as proto:
            async with cls(proto, name, config)._context() as inst:
                yield inst

    async def main(self) -> None:
        """Program entry."""

    @classmethod
    @asynccontextmanager
    async def exec(
        cls: Type[T], name: str, config: JsonObject, *args, **kwargs
    ) -> AsyncIterator[T]:
        """Create an instance from comand-line arguments."""

        async with spawn_exec(
            *args, stdout=asyncio.Queue(), stderr=asyncio.Queue(), **kwargs
        ) as proto:
            async with cls(proto, name, config)._context() as inst:
                yield inst

    @classmethod
    def _write_script(
        cls: Type[T],
        writer: IndentedFileWriter,
        name: str,
        config_path: Path,
        import_str: str,
    ) -> None:
        """Write a script file for running the desired peer program."""

        writer.write("import sys")
        writer.write("from vcorelib.asyncio import run_handle_interrupt")
        writer.write("from vcorelib.io import ARBITER, DEFAULT_INCLUDES_KEY")

        from_str, to_import = import_str_and_item(import_str)
        writer.write(f"from {from_str} import {to_import}")

        fixed_path = str(config_path).replace("\\", "\\\\")
        writer.write(f'CONFIG_PATH = "{fixed_path}"')

        writer.write('if __name__ == "__main__":')
        with writer.indented():
            writer.write(
                f'run_handle_interrupt({to_import}.run("{name}", '
                "ARBITER.decode(CONFIG_PATH, "
                "require_success=True, includes_key=DEFAULT_INCLUDES_KEY"
                ").data, sys.argv))"
            )
            writer.write("sys.exit(0)")

    @classmethod
    @asynccontextmanager
    async def running_program(
        cls: Type[T],
        name: str,
        config: JsonObject,
        import_str: str,
        *args,
        **kwargs,
    ) -> AsyncIterator[T]:
        """Run a peer subprocess."""

        with tempfile(suffix=".json") as config_path:
            # Encode configuration data.
            assert ARBITER.encode(config_path, config)[0]

            # Decode to load includes.
            config = ARBITER.decode(
                config_path,
                require_success=True,
                includes_key=DEFAULT_INCLUDES_KEY,
            ).data
            assert ARBITER.encode(config_path, config)[0]

            with tempfile(suffix=".py") as path:
                # Write file contents.
                with IndentedFileWriter.from_path(
                    path, per_indent=4, linesep="\n"
                ) as writer:
                    cls._write_script(writer, name, config_path, import_str)

                # Run program.
                async with cls.exec(
                    name, config, executable, str(path), *args, **kwargs
                ) as inst:
                    yield inst

    def write(self, data: bytes, addr: tuple[str, int] = None) -> None:
        """Write bytes via this interface."""

        del addr

        self.protocol.stdin.write(data)
        self.stdin_metrics.increment(len(data))

    async def service_queues(self) -> bool:
        """Service data from peer."""

        keep_going = False

        # Forward stderr.
        if self.protocol.stderr_queue is not None:
            keep_going = True
            queue = self.protocol.stderr
            while not queue.empty():
                self.handle_stderr(queue.get_nowait())

        # Handle messages from stdout.
        if self.protocol.stdout_queue is not None:
            keep_going = True
            queue = self.protocol.stdout
            while not queue.empty():
                await self.handle_stdout(queue.get_nowait())

        return keep_going
