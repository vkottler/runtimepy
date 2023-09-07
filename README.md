<!--
    =====================================
    generator=datazen
    version=3.1.3
    hash=658cf5caabd9cdd1e33db33971eb1a47
    =====================================
-->

# runtimepy ([2.6.0](https://pypi.org/project/runtimepy/))

[![python](https://img.shields.io/pypi/pyversions/runtimepy.svg)](https://pypi.org/project/runtimepy/)
![Build Status](https://github.com/vkottler/runtimepy/workflows/Python%20Package/badge.svg)
[![codecov](https://codecov.io/gh/vkottler/runtimepy/branch/master/graphs/badge.svg?branch=master)](https://codecov.io/github/vkottler/runtimepy)
![PyPI - Status](https://img.shields.io/pypi/status/runtimepy)
![Dependents (via libraries.io)](https://img.shields.io/librariesio/dependents/pypi/runtimepy)

*A framework for implementing Python services.*

## Documentation

### Generated

* By [sphinx-apidoc](https://vkottler.github.io/python/sphinx/runtimepy)
(What's [`sphinx-apidoc`](https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html)?)
* By [pydoc](https://vkottler.github.io/python/pydoc/runtimepy.html)
(What's [`pydoc`](https://docs.python.org/3/library/pydoc.html)?)

## Python Version Support

This package is tested with the following Python minor versions:

* [`python3.8`](https://docs.python.org/3.8/)
* [`python3.9`](https://docs.python.org/3.9/)
* [`python3.10`](https://docs.python.org/3.10/)
* [`python3.11`](https://docs.python.org/3.11/)

## Platform Support

This package is tested on the following platforms:

* `ubuntu-latest`
* `macos-latest`
* `windows-latest`

# Introduction

# Command-line Options

```
$ ./venv3.11/bin/runtimepy -h

usage: runtimepy [-h] [--version] [-v] [--curses] [-C DIR]
                 {arbiter,tui,noop} ...

A framework for implementing Python services.

options:
  -h, --help          show this help message and exit
  --version           show program's version number and exit
  -v, --verbose       set to increase logging verbosity
  --curses            whether or not to use curses.wrapper when starting
  -C DIR, --dir DIR   execute from a specific directory

commands:
  {arbiter,tui,noop}  set of available commands
    arbiter           run a connection-arbiter application from a config
    tui               run a terminal interface for the channel environment
    noop              command stub (does nothing)

```

## Sub-command Options

### `arbiter`

```
$ ./venv3.11/bin/runtimepy arbiter -h

usage: runtimepy arbiter [-h] configs [configs ...]

positional arguments:
  configs     the configuration to load

options:
  -h, --help  show this help message and exit

```

### `tui`

```
$ ./venv3.11/bin/runtimepy tui -h

usage: runtimepy tui [-h] [-i ITERATIONS] [-r RATE]

options:
  -h, --help            show this help message and exit
  -i ITERATIONS, --iterations ITERATIONS
                        maximum number of program iterations (if greater than
                        zero, default: 0)
  -r RATE, --rate RATE  frequency (in Hz) to run the interface (default: 60.0
                        Hz)

```

# Internal Dependency Graph

A coarse view of the internal structure and scale of
`runtimepy`'s source.
Generated using [pydeps](https://github.com/thebjorn/pydeps) (via
`mk python-deps`).

![runtimepy's Dependency Graph](im/pydeps.svg)
