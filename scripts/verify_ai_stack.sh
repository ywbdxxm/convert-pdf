#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCLING_VENV="${DOCLING_VENV_DIR:-$REPO_ROOT/docling/.venv}"
ENV_NAME="${AI_BASE_ENV_NAME:-ai-base-cu124-stable}"
ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-$HOME/.mamba}"
MICROMAMBA_BIN="${MICROMAMBA_BIN:-$HOME/.local/bin/micromamba}"

echo "[1/4] verifying WSL GPU"
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader

echo "[2/4] verifying Docker GPU runtime"
docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu24.04 \
  nvidia-smi --query-gpu=name,driver_version --format=csv,noheader

echo "[3/4] verifying shared AI base torch + CUDA"
MAMBA_ROOT_PREFIX="$ROOT_PREFIX" "$MICROMAMBA_BIN" run -n "$ENV_NAME" python - <<'PY'
import torch
print("torch", torch.__version__)
print("cuda_available", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device", torch.cuda.get_device_name(0))
PY

echo "[4/4] verifying Docling overlay"
"$DOCLING_VENV/bin/python" - <<'PY'
import docling
print("docling", getattr(docling, "__version__", "unknown"))
PY
