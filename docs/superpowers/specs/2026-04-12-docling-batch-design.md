# Docling Batch Processor Design

**Date:** 2026-04-12

## Goal
- Build a first-version batch processor that converts embedded-manual PDFs into durable assets that are easy for an AI assistant to read, retrieve, cite, and verify.

## Product Intent
- The output is not "just Markdown".
- The output must preserve enough structure to support:
  - semantic retrieval
  - page-aware citation
  - manual inspection
  - later structured extraction of registers, AF tables, timing limits, and other embedded-specific knowledge

## Docling Best-Practice Alignment
- Use `DocumentConverter.convert_all(..., raises_on_error=False)` for batch execution.
- Treat `Docling JSON` as the canonical intermediate artifact.
- Export `Markdown` as a human-readable companion.
- Generate retrieval chunks from native Docling chunkers, not from post-hoc Markdown splitting.
- Default to `HybridChunker`, with tokenizer/model alignment exposed as configuration.
- Preserve `contextualized_text` for embeddings and downstream generation.
- Keep OCR and page-image generation configurable rather than always-on.

## Scope
### In scope
- Recursive PDF discovery.
- Per-document conversion using Docling.
- Per-document output package:
  - `document.json`
  - `document.md`
  - `manifest.json`
  - `sections.jsonl`
  - `chunks.jsonl`
- Run-level summary file for the whole batch.
- GPU-aware conversion options, including OCR backend configuration.
- Tests for path planning, manifest generation, chunk/section record generation, and CLI parsing.

### Out of scope
- Register/table semantic extraction into domain-specific schemas.
- Vector database ingestion.
- Framework-specific RAG adapters.
- Visual-grounding sidecars beyond placeholder-ready hooks.

## File Layout
- `docling_batch/`
  - Python package for CLI, config, conversion, indexing, and serialization.
- `tests/`
  - Unit tests and a minimal smoke-style test using synthetic data.
- `docs/superpowers/specs/2026-04-12-docling-batch-design.md`
  - Approved design.
- `docs/superpowers/plans/2026-04-12-docling-batch-implementation.md`
  - Implementation plan.

## Output Layout
- `output_root/<doc_id>/document.json`
- `output_root/<doc_id>/document.md`
- `output_root/<doc_id>/manifest.json`
- `output_root/<doc_id>/sections.jsonl`
- `output_root/<doc_id>/chunks.jsonl`
- `output_root/_runs/<timestamp>.json`

## Data Model
### Manifest
- Document identity and provenance:
  - `doc_id`
  - `title`
  - `source_pdf_path`
  - `source_pdf_sha256`
  - `source_filename`
  - `page_count`
  - `docling_version`
  - `status`
- Processing config:
  - `ocr_enabled`
  - `ocr_engine`
  - `force_full_page_ocr`
  - `accelerator_device`
  - `chunker_type`
  - `tokenizer`
- Output references:
  - JSON/Markdown/sections/chunks paths

### Section Index
- One record per logical heading group derived from chunk metadata.
- Required fields:
  - `doc_id`
  - `section_id`
  - `heading_path`
  - `heading_level`
  - `page_start`
  - `page_end`
  - `chunk_count`
  - `text_preview`

### Chunk Index
- One record per Docling native chunk.
- Required fields:
  - `doc_id`
  - `chunk_id`
  - `section_id`
  - `chunk_index`
  - `heading_path`
  - `page_start`
  - `page_end`
  - `text`
  - `contextualized_text`
  - `doc_item_count`
  - `table_like`
  - `citation`

## GPU Strategy
- Default accelerator device should be configurable and default to `cuda`.
- OCR backend should default to `rapidocr` when OCR is enabled.
- OCR itself should not be mandatory for all PDFs.
- First-run model downloads are acceptable but must be explicit in configuration and logs.

## Failure Handling
- Batch conversion continues when one file fails.
- Each document writes status and errors to its manifest.
- The run summary aggregates success/failure/partial-success counts.

## Testing Strategy
- TDD for CLI/config and index-generation logic.
- Tests avoid live network/model downloads by using synthetic chunk/document records or fakes.
- Verification at implementation end includes:
  - unit tests
  - CLI help
  - a minimal no-conversion smoke path if feasible

## Acceptance Criteria
- User can point the tool at a directory of manuals and get per-document JSON/Markdown/index artifacts plus a run summary.
- Chunk index is page-aware and section-aware.
- Output is suitable for later AI retrieval and citation.
- GPU configuration is exposed and wired into Docling pipeline options.
