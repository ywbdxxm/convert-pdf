# Progress

## Current Status

2026-04-13:

- Mainline comparison reduced to `docling_batch`, `Docling` native output, and `OpenDataLoader PDF`.
- `OpenDataLoader` hybrid mode is included because it may improve hard table pages while staying local.
- `OpenDataLoader + LangChain` and `Docling + LlamaIndex/LangChain` are kept only as metadata spot-checks.
- All other parser/UI/RAG tools are deferred.
- Added a dedicated architecture note for `docling_batch` future optimization boundaries.
- OpenDataLoader output handling is now clarified as `raw native output + thin overlay`, not full forced alignment to the current `manuals/processed` schema.
- Added a dedicated architecture note clarifying which `manuals/processed` artifacts are native Docling outputs and which are custom packaging.
- Re-opened the project question from first principles: not "how to extend `docling_batch`", but "what stable output shape best serves future embedded-manual lookup by an agent."
- Audited the current `docling_batch` implementation and the `esp32-s3-technical-reference-manual-en` sample bundle directly.
- Confirmed a concrete structural issue: `manifest.json` currently mixes entrypoint, runtime config, cache status, full table catalog, and full alert payload.
- Confirmed another structural issue: overlapping table records are copied into both `chunks.jsonl` and `sections.jsonl`, creating avoidable duplication.
- Added a new in-progress planning phase focused on reassessing the best-practice output architecture for Docling and OpenDataLoader.
- Read OpenDataLoader official docs directly to ground the comparison in primary sources rather than earlier summary notes.
- Confirmed from official docs that OpenDataLoader JSON is a hierarchical element tree with page-number and bounding-box metadata on elements.
- Confirmed that OpenDataLoader hybrid mode changes extraction quality/enrichment, but not the basic output philosophy of `structured JSON + markdown/html views`.

2026-04-14:

- User clarified the evaluation rule: do not optimize for native-vs-wrapper purity; optimize for the final folder shape that is easiest for Codex to inspect, cite, and verify.
- User narrowed the active comparison set to exactly two production candidates:
  - `docling_batch`
  - `OpenDataLoader PDF hybrid`
- User wants each candidate to have its own method-specific output directory, then be built, improved, compared, and tested end to end.
- User further clarified that each tool must be reconsidered from zero; the previous tool's structure must not implicitly define the next tool's best practice.
- The new working rule is empirical rather than doctrinal: let Codex use both final bundles and decide which one is actually better to work with.
- Wrote the design spec for this direction in `docs/superpowers/specs/2026-04-14-independent-tool-output-design.md`.
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

## Next Action

1. Let the fallback-enabled TRM retry complete.
2. Package and inspect the resulting TRM bundle.
3. Compare first-pass Codex usability of OpenDataLoader vs existing `docling_batch` outputs.
4. Start `docling_batch` output optimization and rename assessment.

## Verification Focus

- `Table 2-9. Peripheral Pin Assignment`
- page numbers
- bounding boxes
- Markdown / JSON / HTML usefulness
- ability to return to the original PDF
- whether Codex direct folder inspection is already sufficient
