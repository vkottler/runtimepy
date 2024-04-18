"""
A sample program for the subprocess manager to invoke.
"""

# built-in
import sys


def main(argv: list[str]) -> int:
    """Program entry."""

    print(argv)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
