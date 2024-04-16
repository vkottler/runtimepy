"""
A sample program for the subprocess manager to invoke.
"""

# built-in
import sys


def message(data) -> None:
    """Send a message to the program that spawned this one."""

    print(data, flush=True)
    print(data, file=sys.stderr, flush=True)


def main(argv: list[str]) -> int:
    """Program entry."""

    message(argv)

    while True:
        data = sys.stdin.read(64)
        if not data:
            break

        message("stdin: " + str(data))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
