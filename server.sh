#!/bin/bash

set -e

PKG=runtimepy

# "./venv$PYTHON_VERSION/bin/$PKG" server -w ${PKG}_http
"./venv$PYTHON_VERSION/bin/$PKG" arbiter -w package://$PKG/server.yaml
