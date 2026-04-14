# Parser Optimization Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refine both `opendataloader_hybrid` and `docling_bundle` into cleaner, lower-noise, more comparable agent-facing bundles.

**Architecture:** Do not change parser scope. Keep both parsers, improve the bundle layer around them, and make comparison more systematic through fixed tasks and clearer quality reporting.

**Tech Stack:** Python 3.12, shell scripts, `unittest`, markdown docs

---

### Task 1: Bundle Reduction

**Files:**
- Modify: `opendataloader_hybrid/bundle.py`
- Modify: `docling_bundle/converter.py`
- Modify: `docling_bundle/reading_bundle.py`
- Modify: `docling_bundle/tables.py`
- Test: `tests/test_opendataloader_bundle.py`
- Test: `tests/test_docling_reading_bundle.py`
- Test: `tests/test_tables.py`

- [ ] Collapse to a single entry file `README.md`.
- [ ] Remove default `pages/` generation.
- [ ] Keep runtime/native/cache state out of the default final bundle.
- [ ] Reduce default table sidecars to a single default format where justified.

### Task 2: OpenDataLoader Quality Alerts

**Files:**
- Modify: `opendataloader_hybrid/bundle.py`
- Test: `tests/test_opendataloader_bundle.py`

- [ ] Add alert generation for pages where a target heading or caption is followed by a large image but no native `table` element.
- [ ] Expose those alerts in `README.md`.
- [ ] Verify with `python3 -m unittest tests.test_opendataloader_bundle -v`.

### Task 3: OpenDataLoader Runtime Visibility

**Files:**
- Modify: `scripts/run_opendataloader_hybrid.sh`
- Modify: `opendataloader_hybrid/bundle.py`
- Test: `tests/test_opendataloader_layout.py`

- [ ] Record whether fallback was triggered.
- [ ] Surface that state through `manifest.json` and `README.md`, not a separate runtime layer by default.
- [ ] Verify with `python3 -m unittest tests.test_opendataloader_layout tests.test_opendataloader_bundle -v`.

### Task 4: Docling Alert Surfacing

**Files:**
- Modify: `docling_bundle/reading_bundle.py`
- Modify: `docling_bundle/converter.py`
- Test: `tests/test_docling_reading_bundle.py`

- [ ] Include page references for alerts in `README.md`.
- [ ] Keep the entry file as the only start point.
- [ ] Verify with `python3 -m unittest tests.test_docling_reading_bundle -v`.

### Task 5: Comparative Task Harness

**Files:**
- Create: `docs/architecture/2026-04-15-parser-comparison-tasks.md`
- Create: `scripts/compare_parser_tasks.sh`
- Update: `README.md`

- [ ] Define a fixed task list for `datasheet` and `TRM` lookups.
- [ ] Add a script or documented command sequence to run and log those comparisons.
- [ ] Link it from the root README.

### Task 6: Evidence-Based Iteration Gate

**Files:**
- Modify: `docs/architecture/2026-04-15-parser-status-and-next-steps.md`
- Modify: `findings.md`
- Modify: `progress.md`

- [ ] Update the current verdict after each optimization batch.
- [ ] Do not add new parser families during this roadmap unless one of the two active paths is clearly blocked.
