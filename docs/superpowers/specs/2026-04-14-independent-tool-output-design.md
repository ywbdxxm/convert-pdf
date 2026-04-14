# Independent Tool Output Design

Date: 2026-04-14

## Goal

Define how this project should evaluate and package the two active manual-processing candidates:

- `docling_batch`
- `OpenDataLoader PDF hybrid`

The design target is not parser purity or schema elegance.

The design target is:

> Which final output bundle is easiest for Codex to read, navigate, cite, and verify against the original PDF during embedded development work?

## Direction Lock

This design intentionally rejects premature unification.

Rules:

1. Each tool must be evaluated from zero.
2. Each tool gets its own method-specific output directory.
3. Do not force one tool's folder structure to define the other's best practice.
4. Final judgment comes from actual Codex usage, not from architectural neatness.
5. The original PDF remains final authority for engineering conclusions.

## Non-Goals

- Do not build a universal schema before evidence exists.
- Do not add RAG, embeddings, vector databases, or chat UI.
- Do not turn `docling_batch` into a generic multi-tool orchestration framework.
- Do not compress OpenDataLoader's rich metadata into a weaker Docling-shaped abstraction.
- Do not treat "native vs custom" separation as a goal by itself.

## Comparison Standard

The two candidates should be judged only on Codex-facing usefulness.

Primary criteria:

- Can Codex quickly find the right entry file?
- Can Codex jump to the relevant page or section with low friction?
- Can Codex inspect table values and visual evidence easily?
- Can Codex preserve page-aware citation?
- Can Codex tell when to distrust the parsed result and return to the PDF?
- Is the bundle small and legible enough to inspect repeatedly without confusion?

Secondary criteria:

- provenance clarity
- long-document resilience
- maintenance burden

## Top-Level Layout

Processed outputs should live under tool-specific roots:

```text
manuals/processed/
  docling_batch/<doc_id>/
  opendataloader_hybrid/<doc_id>/
```

This is the only required cross-tool convention.

Everything below each `<doc_id>` should be decided tool-by-tool.

## `docling_batch` Bundle Design

### Design intent

`docling_batch` is already close to a Codex-facing bundle, but its current folder mixes too many responsibilities and duplicates table metadata too aggressively.

The goal is to improve the bundle as a product for Codex use, not to purify it into "native vs wrapper" layers.

### Recommended bundle shape

```text
manuals/processed/docling_batch/<doc_id>/
  README.generated.md
  quality-summary.md
  document.json
  document.md
  document.html
  manifest.json
  sections.jsonl
  chunks.jsonl
  pages/
  tables/
  tables.index.jsonl
  artifacts/
  alerts.json
  runtime/
    run.json
    cache/
```

### Why this shape fits Docling

- `document.json` remains the canonical structured artifact.
- `document.md` and `document.html` remain the fastest reading views.
- `README.generated.md` becomes the first file Codex should open.
- `quality-summary.md` compresses risk signals into one human/agent-readable page.
- `pages/` solves the common "I know the page number, just show me that page" workflow.
- `tables.index.jsonl` makes table lookup explicit without bloating `manifest.json`.
- `runtime/cache/` moves window-resume state out of the main evidence surface.

### Required improvements over current output

1. Shrink `manifest.json` into a small entry/provenance file.
2. Move full table catalog out of `manifest.json` into `tables.index.jsonl`.
3. Stop embedding full table objects repeatedly into both `chunks.jsonl` and `sections.jsonl`.
4. Add `pages/` page-level slices for direct page lookup.
5. Add `README.generated.md` with recommended reading order and key paths.
6. Add `quality-summary.md` with alert counts, suspicious pages, and verification guidance.
7. Move `_windows/` under `runtime/cache/` so run-state no longer pollutes the stable document bundle.

### `docling_batch` verdict before implementation

Current output is useful, but not yet best practice for Codex.

The biggest remaining problems are:

- too much mixed responsibility in `manifest.json`
- duplicated table metadata
- no dedicated first-open file
- cache/runtime state mixed into the same surface as stable evidence

## `OpenDataLoader PDF hybrid` Bundle Design

### Design intent

`OpenDataLoader hybrid` should be packaged according to its own strengths:

- hierarchical JSON
- page metadata
- bounding boxes
- stronger table extraction on hard pages

The goal is not to imitate Docling.

The goal is to turn OpenDataLoader's strongest evidence into the bundle Codex can use most effectively.

### Recommended bundle shape

```text
manuals/processed/opendataloader_hybrid/<doc_id>/
  README.generated.md
  quality-summary.md
  document.json
  document.md
  document.html
  manifest.json
  pages/
  figures/
  tables/
  elements.index.jsonl
  alerts.json
  runtime/
    run.json
```

### Why this shape fits OpenDataLoader

- `document.json` can stay as the richest evidence tree.
- `elements.index.jsonl` can flatten the most useful navigational metadata from the JSON tree for Codex inspection without discarding hierarchy.
- `pages/` should preserve page-local slices and page-aware references.
- `tables/` and `figures/` should expose sidecars that make hard visual evidence inspectable.
- `README.generated.md` should explain where bbox-heavy evidence lives and how to verify it.
- `quality-summary.md` should highlight where hybrid mode materially improved or still struggled.

### Required evaluation questions before finalizing its bundle

1. Does native `document.json` already make `elements.index.jsonl` unnecessary?
2. Are `document.md` and `document.html` readable enough to be first-line views?
3. Does the tool emit table/image sidecars directly, or do we need thin exports to make them inspectable?
4. Is page-level slicing better derived from JSON or Markdown?
5. Does hybrid mode preserve enough metadata to trace difficult tables back to the original page cleanly?

### `OpenDataLoader hybrid` verdict before implementation

Its best-practice bundle cannot be finalized until we run it on the same manuals and inspect the actual outputs.

What is already clear is:

- it should not be forced into a Docling-shaped schema
- bbox-aware evidence must stay accessible
- its strongest artifact is likely the JSON tree, not a custom chunk index

## Shared Rules That Still Apply

Even though bundles stay independent, a few cross-tool rules are still valid because they come from Codex usage rather than schema ideology.

Each final bundle should have:

- one obvious first-open file
- one concise quality/risk summary
- stable access to the original PDF path
- inspectable table or figure evidence
- an easy page-based lookup path
- runtime/cache state separated from stable evidence files

These are usage requirements, not schema requirements.

## Test Protocol

After both bundles exist, compare them on the same manuals and the same concrete tasks.

Initial test set:

- `esp32-s3_datasheet_en.pdf`
- `esp32-s3_technical_reference_manual_en.pdf`

Core tasks:

1. Find and cite a known pin-assignment table.
2. Find a register description by chapter/section.
3. Verify a timing or electrical table against the original PDF.
4. Inspect a figure-heavy or diagram-heavy page.
5. Recover from a suspicious parse and determine whether the PDF must be opened.

For each task, record:

- number of file opens needed
- whether the right page was found quickly
- whether the needed table/figure was inspectable
- whether citation remained page-aware
- whether Codex had enough confidence to answer or had to fall back to the PDF

## Decision Rule After Testing

Possible outcomes:

1. `docling_batch` remains better overall.
2. `OpenDataLoader hybrid` becomes the new mainline.
3. They are each better for different manual classes, so the project keeps both with explicit routing guidance.

This decision should be made only after empirical bundle use, not before.

## Immediate Next Steps

1. Implement the improved `docling_batch` bundle shape.
2. Install and run `OpenDataLoader PDF hybrid` on the same sample manuals.
3. Build the best Codex-facing OpenDataLoader bundle from the actual outputs.
4. Run the comparison protocol and record findings.
