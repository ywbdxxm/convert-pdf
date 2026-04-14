# Progress

## Current Status

2026-04-13:

- Mainline comparison reduced to `docling_bundle`, `Docling` native output, and `OpenDataLoader PDF`.
- `OpenDataLoader` hybrid mode is included because it may improve hard table pages while staying local.
- `OpenDataLoader + LangChain` and `Docling + LlamaIndex/LangChain` are kept only as metadata spot-checks.
- All other parser/UI/RAG tools are deferred.
- Added a dedicated architecture note for `docling_bundle` future optimization boundaries.
- OpenDataLoader output handling is now clarified as `raw native output + thin overlay`, not full forced alignment to the current `manuals/processed` schema.
- Added a dedicated architecture note clarifying which `manuals/processed` artifacts are native Docling outputs and which are custom packaging.
- Re-opened the project question from first principles: not "how to extend `docling_bundle`", but "what stable output shape best serves future embedded-manual lookup by an agent."
- Audited the current `docling_bundle` implementation and the `esp32-s3-technical-reference-manual-en` sample bundle directly.
- Confirmed a concrete structural issue: `manifest.json` currently mixes entrypoint, runtime config, cache status, full table catalog, and full alert payload.
- Confirmed another structural issue: overlapping table records are copied into both `chunks.jsonl` and `sections.jsonl`, creating avoidable duplication.
- Added a new in-progress planning phase focused on reassessing the best-practice output architecture for Docling and OpenDataLoader.
- Read OpenDataLoader official docs directly to ground the comparison in primary sources rather than earlier summary notes.
- Confirmed from official docs that OpenDataLoader JSON is a hierarchical element tree with page-number and bounding-box metadata on elements.
- Confirmed that OpenDataLoader hybrid mode changes extraction quality/enrichment, but not the basic output philosophy of `structured JSON + markdown/html views`.

2026-04-14:

- User clarified the evaluation rule: do not optimize for native-vs-wrapper purity; optimize for the final folder shape that is easiest for Codex to inspect, cite, and verify.
- User narrowed the active comparison set to exactly two production candidates:
  - `docling_bundle`
  - `OpenDataLoader PDF hybrid`
- User wants each candidate to have its own method-specific output directory, then be built, improved, compared, and tested end to end.
- User further clarified that each tool must be reconsidered from zero; the previous tool's structure must not implicitly define the next tool's best practice.
- The new working rule is empirical rather than doctrinal: let Codex use both final bundles and decide which one is actually better to work with.
- Wrote the initial design spec for the independent-bundle direction and later consolidated it into the current parser status + roadmap docs.
- Self-reviewed the spec to ensure it preserves the "independent bundles first, empirical judgment later" rule.
- Began inline execution in an isolated worktree at `.worktrees/opendataloader-hybrid`.
- Wrote and passed the first OpenDataLoader TDD cycle for:
  - dedicated `opendataloader/` overlay workspace files
  - bootstrap and hybrid runner scripts
  - initial `opendataloader_hybrid` bundle builder with `elements.index.jsonl`, `pages/`, `README.generated.md`, and `quality-summary.md`
- Verified baseline repo tests in the worktree with `python3 -m unittest tests.test_cli tests.test_paths -v`.
- Hit the first real system blocker: OpenDataLoader requires Java 11+, but this WSL system initially had no `java`.
- Java 17 is now installed at the WSL system layer and verified with `java -version`.
- Corrected the first OpenDataLoader environment mistake: the initial bootstrap path tried to duplicate `torch`; the bootstrap script now reuses the shared AI base with `--system-site-packages`.
- Installed `opendataloader-pdf[hybrid]` successfully into the dedicated `opendataloader/.venv`.
- Verified from install logs that `torch` was reused from `/home/qcgg/.mamba/envs/ai-base-cu124-stable`.
- Ran `OpenDataLoader PDF hybrid` on `esp32-s3_datasheet_en.pdf`.
- Observed real hybrid routing behavior: `JAVA=18, BACKEND=69` on the 87-page datasheet.
- Built the first Codex-facing OpenDataLoader bundle under `manuals/processed/opendataloader_hybrid/esp32-s3-datasheet-en/`.
- Fixed two real bundler bugs discovered from the first real sample:
  - support actual OpenDataLoader keys `page number` and `bounding box`
  - copy native `<stem>_images/` sidecar directories into `figures/`
- Fixed a third real bundler bug:
  - clean stale bundle files before rebuilding the same output directory
- OpenDataLoader-specific tests now pass:
  - `python3 -m unittest tests.test_opendataloader_layout tests.test_opendataloader_bundle -v`
- First TRM attempt with OpenDataLoader hybrid failed on a real tool bug:
  - `Comparison method violates its general contract!`
  - backend transform failure after substantial progress through the ESP32-S3 TRM
- Updated the runner to enable `--hybrid-fallback` by default and started a second TRM attempt.
- Second TRM attempt completed successfully because `--hybrid-fallback` prevented total run failure.
- Reworked the OpenDataLoader directory strategy so the visible final tree is only:
  - `manuals/processed/opendataloader_hybrid/<doc_id>/...`
- Native raw files are now stored inside each document bundle under:
  - `runtime/native/`
- The previous top-level staging directory was moved out of `manuals/processed/` into `tmp/opendataloader_hybrid-native`.
- Fixed another bundler bug: when a native staging directory contains multiple documents, bundle selection now follows `source_pdf_path` stem instead of filename sort order.
- Built the TRM OpenDataLoader bundle successfully with:
  - `page_count = 1531`
  - `element_count = 30290`
  - `table_count = 2467`
  - `alert_count = 0`
- Reworked `docling_bundle` output layout to live under `manuals/processed/docling_bundle/<doc_id>/`.
- Added `README.generated.md`, `quality-summary.md`, `pages/`, `tables.index.jsonl`, and `runtime/cache` support to `docling_bundle`.
- Reduced `docling_bundle` chunk/section table duplication by switching from embedded table objects to `table_ids`.
- Re-ran `docling_bundle` on the datasheet and the ESP32-S3 TRM with the new bundle layout.
- Confirmed `docling_bundle` large-TRM run completed successfully with window cache and the new output layout.
- Reached the current comparison verdict:
  - OpenDataLoader hybrid is the stronger extraction/evidence path.
  - `docling_bundle` is the calmer and more immediately usable reading bundle.
  - `docling_batch` has now been renamed to `docling_bundle`.
- Pruned obsolete docs under `docs/` and reduced the active document set to:
  - `docs/README.md`
  - `docs/architecture/2026-04-15-parser-status-and-next-steps.md`
  - `docs/architecture/2026-04-12-docling-embedded-manual-processing.md`
  - `docs/architecture/global-workstation-reference.md`
  - `docs/superpowers/plans/2026-04-15-parser-optimization-roadmap.md`
- Updated the root README to point at the current docs only.

2026-04-15:

- Started a fresh optimization worktree at `.worktrees/final-bundle-optimization`.
- Added tracked empty output roots for `manuals/processed/docling_bundle/` and `manuals/processed/opendataloader_hybrid/`.
- Added `OpenDataLoader` runtime reporting via `runtime/report.json`.
- Updated the `OpenDataLoader` runner to persist `run.log` into native staging.
- Added an `OpenDataLoader` alert for image-backed table pages without a native `table` element.
- Verified on the ESP32-S3 datasheet bundle that:
  - `runtime/report.json` exposes `JAVA=18, BACKEND=69`
  - `alerts.json` flags `Table 2-9. Peripheral Pin Assignment` on page `27`
- Improved `docling_bundle` quality summaries so alert entries now include page references and captions/details.
- Verified on the ESP32-S3 datasheet bundle that `quality-summary.md` now surfaces:
  - `table_caption_followed_by_image_without_sidecar p.27: Table 2-9. Peripheral Pin Assignment`
- Added a dedicated current project layout document:
  - `docs/architecture/2026-04-15-project-structure.md`
- Updated `docs/README.md` and the root `README.md` to point at the new structure doc.
- Reached a practical plateau: current parser/bundle outputs are good enough for real use, and the next likely changes are higher-cost experiments rather than obvious wins.

## Next Action

1. Use the current bundles for real manual work.
2. Reopen parser-output engineering only when a concrete failure or new manual class creates a clear need.

## Verification Focus

- `Table 2-9. Peripheral Pin Assignment`
- page numbers
- bounding boxes
- Markdown / JSON / HTML usefulness
- ability to return to the original PDF
- whether Codex direct folder inspection is already sufficient
