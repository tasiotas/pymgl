#!/bin/bash

# This runs inside a manylinux container and produces CPython 3.13 wheels in
# dist on the host. Release builds made before the release tag exists must set
# PYMGL_RELEASE_VERSION (for example, PYMGL_RELEASE_VERSION=0.5.2).

set -euo pipefail

PYTHON_VERSION=3.13

uv venv /uv/$PYTHON_VERSION.venv --python $PYTHON_VERSION
. /uv/$PYTHON_VERSION.venv/bin/activate
uv pip install setuptools versioneer auditwheel tomli
if [[ -n "${PYMGL_RELEASE_VERSION:-}" ]]; then
    export PYMGL_RELEASE_VERSION
fi
uv build --wheel --python $PYTHON_VERSION --out-dir /wheels
deactivate
rm -rf /uv/*

auditwheel repair /wheels/* -w dist
