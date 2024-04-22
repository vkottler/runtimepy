"""
A sample program for the subprocess manager to invoke.
"""

# built-in
import sys

# third-party
from vcorelib.asyncio import run_handle_interrupt

# internal
from runtimepy.sample.program import SampleProgram

if __name__ == "__main__":
    run_handle_interrupt(SampleProgram.run("state", {}, sys.argv))
    sys.exit(0)
