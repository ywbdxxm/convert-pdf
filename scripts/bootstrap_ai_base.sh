#!/usr/bin/env bash
set -euo pipefail

ENV_NAME="${AI_BASE_ENV_NAME:-ai-base-cu124-stable}"
ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-$HOME/.mamba}"
MICROMAMBA_BIN="${MICROMAMBA_BIN:-$HOME/.local/bin/micromamba}"

if [[ ! -x "$MICROMAMBA_BIN" ]]; then
  echo "micromamba not found at $MICROMAMBA_BIN" >&2
  exit 1
fi

if MAMBA_ROOT_PREFIX="$ROOT_PREFIX" "$MICROMAMBA_BIN" env list | awk '{print $1}' | grep -Fxq "$ENV_NAME"; then
  echo "shared AI base already exists: $ENV_NAME"
  exit 0
fi

echo "creating shared AI base: $ENV_NAME"
MAMBA_ROOT_PREFIX="$ROOT_PREFIX" "$MICROMAMBA_BIN" create -y -n "$ENV_NAME" --channel-priority flexible \
  python=3.12 \
  pytorch::pytorch \
  pytorch::torchvision \
  pytorch::torchaudio \
  pytorch-cuda=12.4
