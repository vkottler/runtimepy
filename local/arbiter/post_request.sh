#!/bin/bash

set -e

# curl -X POST http://localhost:8000/pdu/toggle/outlet.1.on

set -x

curl -X POST http://localhost:8000
curl -X POST http://localhost:8000/a
curl -X POST http://localhost:8000/a/b/c

curl -X POST http://localhost:8000/app/help
curl -X POST http://localhost:8000/app/toggle
curl -X POST http://localhost:8000/app/toggle/asdf
curl -X POST http://localhost:8000/app/toggle/paused
curl -X POST http://localhost:8000/app/toggle/paused
