# OpenDataLoader Workspace

This directory is the project-level OpenDataLoader overlay for `convert-pdf`.

## Purpose

- keep OpenDataLoader-specific Python dependencies isolated from other tools
- keep the hybrid runner reproducible and separate from `docling/`
- give the project one obvious place to manage Java/Python assumptions for OpenDataLoader

## Expected Layout

- `.venv/`
  - project overlay venv for OpenDataLoader
- `requirements.txt`
  - project-private dependencies for OpenDataLoader

## Requirements

- Java 11+
- Python 3.10+

## Bootstrap

From the repository root:

```sh
./scripts/bootstrap_opendataloader_env.sh
```

## Hybrid Run

```sh
./scripts/run_opendataloader_hybrid.sh \
  --input manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf \
  --output manuals/processed/opendataloader_hybrid-native
```

## Activation

Activate only when needed:

```sh
source opendataloader/.venv/bin/activate
```
