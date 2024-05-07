([back](../README.md))

# Scope

This project implements a
[pluggable](https://pop-book.readthedocs.io/en/latest/main/plugable.html)
backbone for [asyncio](https://docs.python.org/3/library/asyncio.html)-based
Python programs: **[load configuration data](#loading-configuration-data),
[initialize runtime environment](#initializing-runtime-environment) and
[execute the configured application](#executing-the-configured-application).**

This project's goal is to support embedded-electronics firmware and software
development workflows.

# Core Runtime Capabilities

## Clients and Servers

TODO: example "loopback" desktop demo using a UDP and TCP-based connection.

It should use some kind of `demo.py` (`app: demo.run`)
`while not app.stop.is_set()` polling.

## Structs

TODO: configure sample struct. Modify in UI, maybe a `demo.run` poller?

## Tasks

TODO: sample sinusoid tasks.

## Processes

TODO: sample peer process interaction.

## Registering Custom Factories

TODO: sample custom driver setup.

## Managing UDP and TCP Port Numbers

TODO: show port override use case.

# Loading Configuration Data

Command-line arguments to `runtimepy` determine what configuration data will
be loaded from disk and how it will be interpreted.

# Initializing Runtime Environment

TODO.

# Executing the Configured Application

TODO.
