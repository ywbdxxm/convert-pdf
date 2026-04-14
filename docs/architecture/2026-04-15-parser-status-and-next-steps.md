# Parser Status And Next Steps

Date: 2026-04-15

## Goal

Record the current state of the two active parser-output paths:

- `docling_bundle`
- `opendataloader_hybrid`

This document is the current source of truth for:

- what has already been proven
- what is still weak
- what should be optimized next

## Current Output Trees

The current visible output roots are:

```text
manuals/processed/docling_bundle/<doc_id>/
manuals/processed/opendataloader_hybrid/<doc_id>/
```

OpenDataLoader native staging files are no longer exposed as a top-level parallel tree.

They now live inside:

```text
manuals/processed/opendataloader_hybrid/<doc_id>/runtime/native/
```

## What Was Proven

### OpenDataLoader hybrid

Environment:

- runs in `opendataloader/.venv`
- reuses shared AI base `torch`
- uses system Java 17
- current best-practice runner is:
  - `docling-fast`
  - `--device cuda`
  - `--hybrid-fallback`

Observed strengths:

- faster first-pass extraction
- less sustained GPU dependence
- stronger page/bbox evidence
- much higher structured table yield

Observed limits:

- large TRMs can hit backend sort/transform failures
- fallback is required for operational reliability on those manuals
- some hard tables still degrade into `image + positioned text`

Measured examples:

- ESP32-S3 datasheet:
  - `87` pages
  - `3187` elements
  - `68` structured tables
  - `0` alerts
- ESP32-S3 TRM:
  - `1531` pages
  - `30290` elements
  - `2467` structured tables
  - `0` alerts

### Docling bundle

Environment:

- runs in `docling/.venv`
- uses explicit window cache for large TRMs

Observed strengths:

- calmer reading experience
- table sidecar workflow is more obvious
- `README.generated.md`, `quality-summary.md`, `pages/`, `tables.index.jsonl`, and alerts form a strong verification bundle
- large-manual run completed without parser crash in this round

Observed limits:

- heavier runtime profile on large manuals
- weaker spatial metadata
- lower structured-table coverage
- known figure/empty-sidecar boundaries remain

Measured examples:

- ESP32-S3 datasheet:
  - `87` pages
  - `71` tables
  - `1` alert
- ESP32-S3 TRM:
  - `1531` pages
  - `668` tables
  - `10` alerts

## Current Verdict

If choosing by evidence extraction power:

- prefer `opendataloader_hybrid`

If choosing by direct Codex reading/verification workflow:

- prefer `docling_bundle`

So the project should currently treat them as complementary:

- `OpenDataLoader hybrid` is the stronger extraction/evidence path
- `docling_bundle` is the stronger reading/verifier path

## Next Optimization Priorities

### Priority 1: OpenDataLoader bundle refinement

Goal:

- preserve OpenDataLoader's evidence strengths while making it calmer to read

Highest-value next steps:

1. add explicit page-level or section-level summaries in `README.generated.md`
2. add quality alerts for pages where a key table appears as `image + paragraph fragments` rather than as a native `table`
3. surface table/image/figure entrypoints more prominently in `quality-summary.md`
4. add a small runtime report documenting when fallback was triggered

### Priority 2: Docling bundle refinement

Goal:

- keep Docling's strong reading flow while exposing more of the evidence layer cleanly

Highest-value next steps:

1. add better page-level entrypoints for alert pages
2. make `quality-summary.md` include page numbers for each alert, not just counts
3. trim low-value tables such as repeated index/TOC tables from first-class emphasis
4. optionally add a lightweight page-evidence index for hard pages, without trying to recreate full bbox semantics

### Priority 3: Comparative task harness

Goal:

- stop relying on qualitative memory for comparisons

Highest-value next steps:

1. define 5-8 fixed lookup tasks
2. record for each bundle:
   - files opened
   - time to locate evidence
   - whether page-aware citation survived
   - whether the final answer still required opening the original PDF

## Rename Decision

The package rename is now complete:

- old name: `docling_batch`
- new name: `docling_bundle`

Current recommendation:

- keep this new name
- do not do more naming churn until the parser strategy itself changes
