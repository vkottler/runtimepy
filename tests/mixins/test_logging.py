"""
Test the 'mixins.logging' module.
"""

# built-in
from contextlib import AsyncExitStack

# third-party
from pytest import mark
from vcorelib.logging import LoggerMixin
from vcorelib.paths.context import tempfile

# module under test
from runtimepy.mixins.logging import LogCaptureMixin


class SampleLogger(LoggerMixin, LogCaptureMixin):
    """A sample class."""


@mark.asyncio
async def test_log_capture_mixin_basic():
    """Test basic interactions with a log capture."""

    inst = SampleLogger()

    async with AsyncExitStack() as stack:
        path = stack.enter_context(tempfile())
        writer = stack.enter_context(path.open("w"))

        await inst.init_log_capture(stack, [("info", path)])
        await inst.dispatch_log_capture()

        for _ in range(10):
            writer.write("Hello, world!\n")
            writer.flush()
            await inst.dispatch_log_capture()

        await inst.dispatch_log_capture()
