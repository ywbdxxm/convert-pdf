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
- Wrote a formal Chinese executive report for stakeholders:
  - `docs/architecture/2026-04-15-executive-project-report.md`

2026-04-14 / 2026-04-15 clean rerun wave:

- Began a clean regeneration wave focused only on `ESP32-S3 datasheet` and `ESP32-S3 TRM`.
- Verified that the long-running `OpenDataLoader PDF hybrid` TRM job completed successfully in the current workspace.
- Confirmed the real runtime behavior for the TRM rerun:
  - triage summary: `JAVA=173, BACKEND=1,358`
  - backend processing later failed with `Comparison method violates its general contract!`
  - `--hybrid-fallback` then allowed the run to finish and export final `json/md/html`
- Identified a bundle integrity gap:
  - `runtime/report.json` could be generated from `native_dir/run.log`
  - but the final bundle did not always preserve `run.log` under `runtime/native/`
- Fixed the gap in `opendataloader_hybrid.bundle` so `run.log` is copied into the final bundle when present.
- Added a regression assertion to `tests/test_opendataloader_bundle.py` for `runtime/native/run.log`.
- Re-ran `python3 -m unittest tests.test_opendataloader_bundle -v` and confirmed all `10` tests pass.
- Tried to clean-rerun `OpenDataLoader` datasheet and TRM in parallel with separate native staging directories.
- Found a real execution hazard:
  - both invocations started `docling-fast` backend on the default port `5002`
  - the second backend could not bind the port
  - the datasheet run still completed cleanly
  - the TRM run later lost backend connectivity and fell back heavily to Java
- Decision:
  - keep the clean datasheet rerun
  - discard the contaminated TRM rerun
  - rerun the TRM alone so the hybrid backend has exclusive control and the final output is trustworthy
- User reviewed the generated `OpenDataLoader` bundle directly and identified a more fundamental quality failure:
  - `document.md` still points at native `*_images/` paths that do not exist inside the final bundle
  - the final bundle also still contains a full native-output duplicate under `runtime/native/`
- Root-cause conclusion:
  - this is not just a small bug
  - the bundle design drifted toward “debug/export convenience” instead of “agent-first final product”
- Locked new `OpenDataLoader` bundle principles with failing tests:
  - final `document.md` and `document.html` must only reference bundle-local `figures/`
  - final `runtime/` must keep only minimal execution evidence, not a full native duplicate
  - `manifest.json` must not expose transient `native_dir` / staging paths
- Confirmed `docling_bundle` has the same class of design issue at the architecture level:
  - current implementation always points window-cache writes at `runtime/cache/` inside the final bundle
  - current `manifest.json` mixes document identity with parser/runtime/cache details and output file paths
  - unlike the current `OpenDataLoader` bug, `docling_bundle` appears more self-consistent on image paths, but it still violates the same agent-first bundle boundary principle
- Reassessment correction:
  - the earlier conclusion that the project was already near the optimization ceiling was wrong
  - the real mistake was treating “currently usable” as “already close to best practice for Codex / Claude Code”
  - the bundle audit only became strict enough after direct user review of concrete outputs
- Current corrected position:
  - both output lines still had meaningful, not marginal, agent-first design defects
  - `OpenDataLoader` had self-consistency failures in the final product
  - `docling_bundle` had bundle-boundary failures by mixing final artifacts with runtime/cache concerns
- Continued stricter bundle reduction based on the agent-first audit:
  - switched `OpenDataLoader` to a single entry file `README.md`
  - removed default `pages/` generation from the `OpenDataLoader` bundle
  - kept only `document.{md,json,html}`, one navigation layer, table sidecars, visual assets, alerts, and minimal runtime evidence
  - switched `docling_bundle` to a single entry file `README.md`
  - removed default `pages/` generation from `docling_bundle`
  - moved `docling_bundle` window cache fully out of `manuals/processed/` into `tmp/docling_bundle-cache`
  - began reducing `docling_bundle` default table sidecars toward a single default format
- Re-ran repository tests against the updated agent-first structure in `docling/.venv` and confirmed the currently updated suite passes before the next clean regeneration wave.
- Continued the second reduction wave:
  - unified the visual asset directory name toward `assets/`
  - reduced `docling_bundle` default table sidecars to a single default CSV sidecar format
  - removed `OpenDataLoader` runtime files from the default final bundle and folded the needed state into `README.md` / `manifest.json`
- Re-ran the broader structural test set and confirmed it passes after the newer reductions.
- Cleared old generated outputs again and started a clean regeneration wave using the newest bundle structure.
- Rebuilt `OpenDataLoader` datasheet and TRM bundles with the newer default structure.
- Confirmed the regenerated `OpenDataLoader` datasheet bundle now has:
  - single entry file `README.md`
  - no `pages/`
  - no `runtime/`
  - unified `assets/`
  - only CSV table sidecars
- Rebuilt `docling_bundle` datasheet bundle with the newer default structure and confirmed it now has:
  - single entry file `README.md`
  - no `pages/`
  - no `quality-summary.md`
  - no `runtime/cache/`
  - unified `assets/`
  - only CSV table sidecars
- Rebuilt `docling_bundle` TRM bundle with the same reduced default structure.
- Measured regenerated bundle reality after the reduction wave:
  - `opendataloader_hybrid` datasheet: `5.2M`
  - `opendataloader_hybrid` TRM: `53M`
  - `docling_bundle` datasheet: `16M`
  - `docling_bundle` TRM: `203M`
- The next clear optimization target is no longer `pages/`.
- Even though `assets/` dominates bundle size for some bundles, the project now explicitly keeps full extracted visual evidence by default rather than applying heuristic pruning.
- So the next optimization focus shifts to:
  - reducing remaining consumption-layer noise
  - converging agent-facing navigation/entry behavior
  - preserving evidence completeness while lowering decision overhead for the agent

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

2026-04-15 documentation cleanup wave:

- re-anchored the session with `planning-with-files` and catchup output before editing docs
- audited active docs for stale references to deleted bundle layers and obsolete names
- removed the archived executive report that still contained large amounts of obsolete structure guidance
- updated root docs and active architecture/status/roadmap docs to describe only the current production bundle shape
- corrected measured alert counts in the status doc from the real local manifests/alerts files
- reduced repeated “old structure” language in the root Chinese report and comparison doc
- ran the structural test suite again:
  - `docling/.venv/bin/python -m unittest tests.test_opendataloader_bundle tests.test_docling_reading_bundle tests.test_paths tests.test_workflow tests.test_tables tests.test_images tests.test_alerts tests.test_indexing -v`
  - result: `49` tests passed
