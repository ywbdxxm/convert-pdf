#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: run_opendataloader_hybrid.sh --input <pdf-or-dir> --output <dir> [options]

Options:
  --input <path>         Input PDF or directory. Repeatable.
  --output <dir>         Output directory for native OpenDataLoader files.
  --port <port>          Hybrid backend port. Default: 5002.
  --hybrid-mode <mode>   Hybrid mode. Default: auto.
  --device <device>      Hybrid backend device. Default: cuda.
  --force-ocr            Enable OCR in hybrid backend.
  --no-hybrid-fallback   Disable Java fallback when the hybrid backend fails.
  --help                 Show this help message.
EOF
}

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ODL_VENV_DIR="${ODL_VENV_DIR:-$REPO_ROOT/opendataloader/.venv}"
PORT=5002
HYBRID_MODE="auto"
DEVICE="cuda"
FORCE_OCR=0
HYBRID_FALLBACK=1
INPUTS=()
OUTPUT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --input)
      INPUTS+=("$2")
      shift 2
      ;;
    --output)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    --hybrid-mode)
      HYBRID_MODE="$2"
      shift 2
      ;;
    --device)
      DEVICE="$2"
      shift 2
      ;;
    --force-ocr)
      FORCE_OCR=1
      shift
      ;;
    --no-hybrid-fallback)
      HYBRID_FALLBACK=0
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ ${#INPUTS[@]} -eq 0 || -z "$OUTPUT_DIR" ]]; then
  usage >&2
  exit 1
fi

if [[ ! -x "$ODL_VENV_DIR/bin/opendataloader-pdf" || ! -x "$ODL_VENV_DIR/bin/opendataloader-pdf-hybrid" ]]; then
  echo "OpenDataLoader CLI not found in $ODL_VENV_DIR; run ./scripts/bootstrap_opendataloader_env.sh first" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"
LOG_PATH="$OUTPUT_DIR/run.log"

SERVER_ARGS=(--port "$PORT" --device "$DEVICE")
if [[ "$FORCE_OCR" -eq 1 ]]; then
  SERVER_ARGS+=(--force-ocr)
fi

CLIENT_ARGS=(
  --output-dir "$OUTPUT_DIR"
  --format markdown,json,html
  --hybrid docling-fast
  --hybrid-mode "$HYBRID_MODE"
)
if [[ "$HYBRID_FALLBACK" -eq 1 ]]; then
  CLIENT_ARGS+=(--hybrid-fallback)
fi

"$ODL_VENV_DIR/bin/opendataloader-pdf-hybrid" "${SERVER_ARGS[@]}" &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT

sleep 3

"$ODL_VENV_DIR/bin/opendataloader-pdf" \
  "${CLIENT_ARGS[@]}" \
  "${INPUTS[@]}" 2>&1 | tee "$LOG_PATH"
