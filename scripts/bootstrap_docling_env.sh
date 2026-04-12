#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCLING_DIR="${DOCLING_DIR:-$REPO_ROOT/docling}"
VENV_DIR="${DOCLING_VENV_DIR:-$DOCLING_DIR/.venv}"
ENV_NAME="${AI_BASE_ENV_NAME:-ai-base-cu124-stable}"
ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-$HOME/.mamba}"
MICROMAMBA_BIN="${MICROMAMBA_BIN:-$HOME/.local/bin/micromamba}"

mkdir -p "$DOCLING_DIR"

if [[ ! -d "$VENV_DIR" ]]; then
  echo "creating docling overlay venv: $VENV_DIR"
  MAMBA_ROOT_PREFIX="$ROOT_PREFIX" "$MICROMAMBA_BIN" run -n "$ENV_NAME" \
    python -m venv --system-site-packages "$VENV_DIR"
fi

echo "installing docling project packages into overlay"
uv pip install --python "$VENV_DIR/bin/python" -r "$DOCLING_DIR/requirements.txt"
