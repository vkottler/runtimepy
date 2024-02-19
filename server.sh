#!/bin/bash

set -e

"./venv$PYTHON_VERSION/bin/runtimepy" server -w runtimepy_http
