#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ODL_DIR="${ODL_DIR:-$REPO_ROOT/opendataloader}"
VENV_DIR="${ODL_VENV_DIR:-$ODL_DIR/.venv}"
ENV_NAME="${AI_BASE_ENV_NAME:-ai-base-cu124-stable}"
ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-$HOME/.mamba}"
MICROMAMBA_BIN="${MICROMAMBA_BIN:-$HOME/.local/bin/micromamba}"

mkdir -p "$ODL_DIR"

if ! command -v java >/dev/null 2>&1; then
  echo "java not found; install Java 11+ before using OpenDataLoader" >&2
  exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "creating opendataloader overlay venv: $VENV_DIR"
  MAMBA_ROOT_PREFIX="$ROOT_PREFIX" "$MICROMAMBA_BIN" run -n "$ENV_NAME" \
    python -m venv --system-site-packages "$VENV_DIR"
fi

echo "installing OpenDataLoader project packages into overlay"
"$VENV_DIR/bin/python" -m pip install -U pip
"$VENV_DIR/bin/python" -m pip install -r "$ODL_DIR/requirements.txt"

echo "java version:"
java -version

echo "OpenDataLoader version:"
"$VENV_DIR/bin/python" -m pip show opendataloader-pdf
