#!/bin/bash

set -e

# --no-uvloop
sudo chrt 90 "./venv$PYTHON_VERSION/bin/runtimepy" \
	-C local/arbiter arbiter test.yaml
