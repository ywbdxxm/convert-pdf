# Parser Optimization Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep both active parser-output paths aligned with the current agent-first bundle standard, while focusing only on improvements that still have a clear payoff.

**Architecture:** Do not expand parser scope. Keep `docling_bundle` and `opendataloader_hybrid` as the only active production paths. The bundle reduction wave is already complete; current work should focus on comparison rigor, alert quality, and low-noise navigation improvements.

**Tech Stack:** Python 3.12, shell scripts, `unittest`, markdown docs

---

### Task 1: Bundle Baseline Lock

**Files:**
- Reference: `README.md`
- Reference: `docs/architecture/2026-04-15-parser-status-and-next-steps.md`
- Reference: `docs/architecture/2026-04-15-project-structure.md`

- [x] Single entry file is `README.md`.
- [x] Default final bundles no longer expose `pages/`.
- [x] Runtime/native/cache state stays outside default final bundles.
- [x] Default table sidecar format is CSV.

### Task 2: Comparative Task Harness

**Files:**
- Create: `docs/architecture/2026-04-15-parser-comparison-tasks.md`
- Create: `scripts/compare_parser_tasks.sh`
- Update: `README.md`

- [ ] Define a fixed lookup task list for `datasheet` and `TRM` bundle comparisons.
- [ ] Record objective comparison fields:
  - opened files
  - time to first usable evidence
  - whether page-aware citation survived
  - whether the answer still required opening the original PDF
- [ ] Link the task harness from the root README.

### Task 3: OpenDataLoader Alert Coverage

**Files:**
- Modify: `opendataloader_hybrid/bundle.py`
- Test: `tests/test_opendataloader_bundle.py`

- [ ] Expand alert coverage beyond the current image-backed hard-table pattern where a clear low-noise rule exists.
- [ ] Keep alert output small and action-oriented in `README.md` and `alerts.json`.
- [ ] Verify with `python3 -m unittest tests.test_opendataloader_bundle -v`.

### Task 4: Docling Navigation And Alert Quality

**Files:**
- Modify: `docling_bundle/reading_bundle.py`
- Modify: `docling_bundle/converter.py`
- Test: `tests/test_docling_reading_bundle.py`

- [ ] Keep the entry file as the only start point.
- [ ] Continue improving alert wording only when it reduces inspection cost.
- [ ] Evaluate whether `sections.jsonl + chunks.jsonl` should eventually converge toward a single locator layer.
- [ ] Verify with `python3 -m unittest tests.test_docling_reading_bundle -v`.

### Task 5: Evidence-Based Iteration Gate

**Files:**
- Modify: `docs/architecture/2026-04-15-parser-status-and-next-steps.md`
- Modify: `findings.md`
- Modify: `progress.md`

- [ ] Update the current verdict only after a measured comparison or a real bundle defect.
- [ ] Do not add new parser families during this roadmap unless one of the two active paths is clearly blocked.
