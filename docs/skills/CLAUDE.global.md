# Global CLAUDE.md (user-level)

## Embedded / chip-manual tasks

When a question touches **ESP32 / ESP32-S3 / ESP32-C3 / STM32 / MCU datasheets, TRMs, registers, pins, GPIO mux, peripherals (UART / I2C / SPI / USB / Wi-Fi / BLE), electrical characteristics, timing, boot mode, clock trees, interrupt maps** — or involves **writing embedded firmware / HAL / driver / bring-up code** — or names specific chip identifiers (e.g. `GPIO14`, `VDD_SPI`, `I2C_SCL_ST_TO_INT_RAW`):

**Invoke the `using-manual-bundles` skill before anything else.**

The skill carries the central bundle root, 3-step consumption flow, 4-axis navigation recipes, citation format, and raw-PDF fallback rules. Do not improvise — load the skill.

## AI workstation environment tasks

When a task touches **Python / venv / uv / micromamba / conda / pip / mirror config**, **PyTorch / CUDA / GPU / NVIDIA driver**, **Docker / NVIDIA Container Toolkit**, **model caches / `HF_HOME` / `~/.cache/...`**, or **shell init / activation / `~/.bashrc`** — or the user asks to install / upgrade / repair / verify an AI Python environment, or runs `pip install` / `uv add` / `micromamba install` touching `torch` / `transformers` / `vllm` / `flash-attn` / similar:

**Invoke the `ai-workstation-architecture` skill before running any install, activate, or config edit.**

The skill carries the 6-layer model, tool-to-layer mapping, mirror policy (domestic-mirror-first is the default network posture — swap every swappable channel before the first install), re-anchor commands, known pitfalls, and hard rules. It is machine-portable — the architecture transfers across hosts; installed versions, env names, and paths are per-host and must be re-anchored on entry. Do not improvise — load the skill.
