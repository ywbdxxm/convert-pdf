# Project Structure

Date: 2026-04-15

## Goal

Explain what each top-level directory in this repository is for, and which ones matter for day-to-day work.

This document is the fastest way to re-orient when returning to the project.

## Top-Level Layout

```text
convert-pdf/
  AGENTS.md
  README.md
  docling/
  docling_bundle/
  docs/
  manuals/
  opendataloader/
  opendataloader_hybrid/
  progress.md
  scripts/
  task_plan.md
  tests/
  findings.md
  tmp/
```

## Directory Roles

### `docling/`

Project-level Python overlay environment for Docling.

Contains:

- `README.md`
- `requirements.txt`
- local overlay venv when bootstrapped

Use it for:

- running `python -m docling_bundle ...`
- Docling-specific dependency isolation

### `docling_bundle/`

The Docling-side product code.

This is no longer just a batch experiment directory.

Its current role is:

- turn Docling outputs into a Codex-facing reading and verification bundle

Key responsibilities:

- conversion orchestration
- chunk / section indexes
- table sidecars
- page slices
- quality summary and entry files
- runtime cache layout

### `opendataloader/`

Project-level Python overlay environment for OpenDataLoader.

Contains:

- `README.md`
- `requirements.txt`
- local overlay venv when bootstrapped

Use it for:

- running `opendataloader-pdf`
- running `opendataloader-pdf-hybrid`

### `opendataloader_hybrid/`

The OpenDataLoader-side product code.

Its current role is:

- take OpenDataLoader native outputs
- build a Codex-facing bundle around them

Key responsibilities:

- native file selection
- `elements.index.jsonl`
- page slices
- structured table exports
- runtime/native preservation
- runtime report generation
- quality alerts for hard pages

### `manuals/raw/`

Immutable input PDFs organized by vendor / chip.

Current important samples:

- `manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf`
- `manuals/raw/espressif/esp32s3/esp32-s3_technical_reference_manual_en.pdf`
- `manuals/raw/st/stm32h7/stm32h743vi.pdf`

### `manuals/processed/`

Final visible output bundles for Codex use.

Current active roots:

```text
manuals/processed/docling_bundle/<doc_id>/
manuals/processed/opendataloader_hybrid/<doc_id>/
```

These are the only processed roots that should matter to users.

#### `manuals/processed/docling_bundle/<doc_id>/`

Typical contents:

- `README.generated.md`
- `quality-summary.md`
- `document.json`
- `document.md`
- `document.html`
- `sections.jsonl`
- `chunks.jsonl`
- `tables.index.jsonl`
- `pages/`
- `tables/`
- `artifacts/`
- `alerts.json`
- `runtime/cache/`

#### `manuals/processed/opendataloader_hybrid/<doc_id>/`

Typical contents:

- `README.generated.md`
- `quality-summary.md`
- `document.json`
- `document.md`
- `document.html`
- `elements.index.jsonl`
- `tables.index.jsonl`
- `pages/`
- `tables/`
- `figures/`
- `alerts.json`
- `runtime/report.json`
- `runtime/native/`

### `tmp/`

Explicitly non-final staging area.

Current main use:

- `tmp/opendataloader_hybrid-native/`

This holds OpenDataLoader native intermediate files before bundling.

It should not be treated as the final interface for Codex use.

### `scripts/`

Operational shell entrypoints.

Current important scripts:

- `bootstrap_ai_base.sh`
- `bootstrap_docling_env.sh`
- `bootstrap_opendataloader_env.sh`
- `run_opendataloader_hybrid.sh`
- `verify_ai_stack.sh`

### `tests/`

Repository regression tests.

Current test coverage focuses on:

- path layout
- bundle generation
- parser runner assumptions
- indexing behavior
- quality summary / reading helpers

### `docs/`

Current project documentation set.

Use [docs/README.md](../README.md) from the repository root, or this directory's own [index](../README.md) for navigation.

The current active docs are intentionally small:

- `docs/README.md`
- `docs/architecture/2026-04-12-docling-embedded-manual-processing.md`
- `docs/architecture/2026-04-15-parser-status-and-next-steps.md`
- `docs/architecture/2026-04-15-project-structure.md`
- `docs/architecture/global-workstation-reference.md`
- `docs/superpowers/plans/2026-04-15-parser-optimization-roadmap.md`

### `task_plan.md`, `findings.md`, `progress.md`

Persistent planning files for Codex.

- `task_plan.md`: phase tracking and decisions
- `findings.md`: research and conclusions
- `progress.md`: session-by-session execution log

## Practical Entry Order

If starting fresh, read in this order:

1. `README.md`
2. `docs/README.md`
3. `docs/architecture/2026-04-15-parser-status-and-next-steps.md`
4. this file
5. then whichever processed bundle you actually need

## What Is Stable vs Volatile

Stable:

- `manuals/raw/`
- `manuals/processed/docling_bundle/`
- `manuals/processed/opendataloader_hybrid/`
- `docling_bundle/`
- `opendataloader_hybrid/`

Volatile:

- `tmp/`
- local venv contents in `docling/.venv` and `opendataloader/.venv`
- active planning notes while a phase is still moving

## Current Rule Of Thumb

If a file or directory does not clearly improve Codex lookup, citation, or verification, it probably should not be part of the visible final bundle.
