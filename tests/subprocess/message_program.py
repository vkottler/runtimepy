"""
A sample program for the subprocess manager to invoke.
"""

# built-in
import sys

# third-party
from vcorelib.asyncio import run_handle_interrupt
from vcorelib.io import ARBITER

# internal
from runtimepy.subprocess.sample import SampleProgram

if __name__ == "__main__":
    print(ARBITER.decode("").data)
    run_handle_interrupt(SampleProgram.run("state", {}, sys.argv))
    sys.exit(0)
