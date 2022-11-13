#!./venv3.10/bin/python

"""
A script for testing curses programs.
"""

# built-in
import curses
import sys
from typing import List


def gui(stdscr: curses.window, *_: str) -> None:
    """TODO."""

    stdscr.clear()

    stdscr.box()
    stdscr.addstr(1, 1, str(stdscr))
    stdscr.addstr(2, 1, "Hello")
    stdscr.addstr(3, 1, "World!")

    stdscr.refresh()
    stdscr.getkey()


def main(argv: List[str]) -> int:
    """Program entry-point."""

    curses.wrapper(gui, *argv)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
