# Findings

## Current Direction

The mainline is intentionally narrow:

1. `docling_bundle` existing output as frozen baseline
2. `Docling` native output
3. `OpenDataLoader PDF` local mode
4. `OpenDataLoader PDF` hybrid mode with local `docling-fast`

Optional metadata spot-checks only:

5. `OpenDataLoader PDF + LangChain`
6. `Docling + LlamaIndex / LangChain`

Everything else is deferred.

## Why This Narrowing

The project is not trying to evaluate the whole ecosystem.

The focused question is:

> For agentic file retrieval on local chip manuals, is `Docling` or `OpenDataLoader PDF` the better path?

Preferred architecture:

```text
PDF -> parser -> structured files -> Codex reads the folder -> original PDF verification
```

## Baseline

`docling_bundle` is useful only as a baseline:

- existing outputs already exist
- no new features should be added
- it is there only to measure whether external tools actually reduce custom code

If later unfrozen, only thin file-navigation improvements are acceptable:

- page-level files
- folder entrypoint
- quality summary
- optional hard-page images
- Docling-native chunk export for comparison

Not acceptable:

- RAG/search/vector DB
- more parser heuristics
- VLM rescue pipelines
- UI/application logic

## Main Comparison Focus

- page citation
- source path
- bounding boxes or equivalent spatial metadata
- table visibility and inspectability
- raw file readability by Codex
- ability to return to the original PDF page

The original PDF remains final authority for engineering conclusions.

## OpenDataLoader Output Handling

The current `manuals/processed/<doc_id>` layout is not a universal best practice.

It is better understood as:

- a good `docling_bundle`-specific bundle
- a useful example of agent-friendly affordances
- not a schema every parser should be forced into immediately

What is worth preserving from the current layout:

- one obvious directory per document
- both human-readable and machine-readable outputs
- clear provenance
- explicit table/image sidecars
- explicit quality/risk signaling

What should not be treated as universal:

- our exact `manifest.json` shape
- our exact `chunks.jsonl` / `sections.jsonl` schema
- our exact `alerts.json` semantics
- our exact table-link injection strategy
- our exact `_windows/` cache layout

For OpenDataLoader, the better rule is:

1. keep raw OpenDataLoader outputs intact
2. add only a thin agent-friendly overlay when needed
3. do not normalize away useful native metadata too early

Recommended output handling for OpenDataLoader:

- `raw/`
  - untouched OpenDataLoader JSON / Markdown / HTML / assets
- `overlay/`
  - small, optional, agent-friendly files derived from raw outputs

The overlay should stay minimal:

- `README.generated.md` or `index.json` for entrypoint
- optional `pages/` page-level slices
- optional `quality-summary.md`
- optional normalized links to important raw files

This means:

- OpenDataLoader should not be forced to fully match the current `manuals/processed` architecture up front
- parts of the current architecture remain useful as design inspiration
- the likely best practice is `raw native output + thin overlay`, not a full schema rewrite

## Current `docling_bundle` Bundle Weak Points

Fresh code + sample inspection on `2026-04-13` shows a few concrete problems in the current bundle shape.

### 1. `manifest.json` mixes too many responsibilities

It currently combines:

- document identity and provenance
- runtime/configuration details
- window-cache status
- output path entrypoints
- full table catalog
- full alert payload

For a large TRM this becomes unnecessarily heavy.

Example from the ESP32-S3 TRM bundle:

- `table_count = 667`
- full `tables[]` is embedded directly in `manifest.json`
- full `alerts[]` is also embedded directly in `manifest.json`

This suggests `manifest.json` should likely become a small entrypoint plus references to separate indexes, not the container for every secondary dataset.

### 2. Table metadata is duplicated into chunk/section records

`attach_table_references()` currently copies overlapping table objects into every chunk and section record based on page overlap.

This is convenient, but it creates high fan-out duplication:

- the same table record appears in `manifest.json`
- and again in many `chunks.jsonl` rows
- and again in many `sections.jsonl` rows

This is probably acceptable for a small document, but not a clean long-term shape for large manuals.

Likely better pattern:

- keep one canonical `tables.index.jsonl`
- chunk/section rows carry only `table_ids` or no inline table attachment by default

### 3. Entry layer, evidence layer, and run/cache layer are mixed together

Current single-folder layout mixes:

- reading assets: `document.md`, `document.html`
- canonical parser asset: `document.json`
- evidence sidecars: `tables/`, `artifacts/`
- retrieval/index layer: `chunks.jsonl`, `sections.jsonl`
- quality layer: `alerts.json`
- runtime/cache layer: `_windows/`

This is practical but blurs what is:

- native parser output
- stable evidence
- derived overlay
- transient execution state

The likely better separation is:

- raw/native parser output
- overlay/navigation/index files
- run/cache state outside the stable document bundle

### 4. Current bundle is agent-friendly but not comparison-friendly

The current design is optimized for immediate use, but it obscures tool comparison because it hides where:

- Docling ends
- `docling_bundle` packaging begins
- heuristics and filtering affect the result

For A/B parser evaluation, native/raw preservation should be explicit.

## OpenDataLoader Official Facts

Direct review of the official GitHub README and docs confirms a few important points.

### 1. OpenDataLoader's native JSON is already a hierarchical evidence format

Official JSON schema says:

- root includes document metadata such as `file name`, `number of pages`, author/title/dates
- root `kids` contains top-level content elements
- every content element includes `type`, `page number`, and `bounding box`
- tables are hierarchical with rows/cells and cell spans
- captions can link to related content IDs
- images can reference external image files or embedded/base64 payloads

This means OpenDataLoader's native JSON is closer to a directly consumable evidence tree than our current `manifest + chunks + sections` split.

### 2. OpenDataLoader's native philosophy is "rich parser output first"

Official docs consistently position the outputs as:

- `json` for structured data with metadata and bounding boxes
- `markdown` for LLM context/chunking
- `html` for human/web display
- optional annotated PDF for visual debugging

This is much closer to:

- one canonical native document tree
- multiple presentation/consumption views

than to:

- one large custom bundle with multiple derived indexes embedded up front

### 3. Hybrid mode is not a new storage format

Official hybrid docs describe hybrid as a routing/extraction mode:

- default `--hybrid-mode auto`: dynamic triage
- `--hybrid-mode full`: all pages to backend
- backend adds OCR/formula/picture-description capabilities
- formula and picture-description enrichments are surfaced back into normal JSON/Markdown output

So for architecture purposes, hybrid mode changes extraction quality and optional fields, not the fundamental output philosophy.

### 4. OpenDataLoader strongly assumes downstream chunking happens after parsing

Its RAG guide explicitly shows:

- convert PDF to `json,markdown`
- load `document.json`
- chunk by semantic elements or sections downstream
- carry `page number` and `bounding box` metadata into retrieval

This reinforces a key design lesson for this project:

- parser output and retrieval/index design should be separated
- chunk indexes do not have to be first-class artifacts in the stable document bundle

### 5. Benchmark claims support testing hybrid for hard table pages, but not blindly adopting its worldview

Official benchmark pages claim:

- `OpenDataLoader [hybrid]` ranks first for table structure
- `Docling` ranks second and remains strong on headings
- local `OpenDataLoader` without hybrid is much weaker on table structure

So the right comparison target for embedded manuals is indeed:

- current Docling path
- OpenDataLoader hybrid path for hard tables

not local-only OpenDataLoader as the final answer by default.

## 2026-04-14 Direction Lock

The user explicitly rejected premature schema unification.

The active rule is now:

- each tool gets its own independently designed output bundle
- each tool should be judged from zero on what best serves Codex usage
- do not let the previous tool's structure bias the next tool's "best practice"
- final judgment comes from actual Codex lookup/citation/verification experience

This changes the design target from:

- "find one universal schema first"

to:

- "build the best Codex-facing bundle for each tool separately, then compare them empirically"

Implication:

- `docling_bundle` should be improved according to its own strengths and weaknesses
- `OpenDataLoader hybrid` should be packaged according to its own strengths and weaknesses
- only after both are built and tested should cross-tool common patterns be extracted

## 2026-04-15 Stricter Agent-First Bundle Audit

Direct inspection of the regenerated `ESP32-S3 datasheet` bundles shows the project was still not at best practice.

### 1. `pages/` is currently over-produced by default

Observed on the datasheet:

- `opendataloader_hybrid` bundle: `235` files total
- `docling_bundle` bundle: `324` files total
- `pages/` alone adds `87` extra markdown files for each bundle

This is a large file-count increase for a weakly justified benefit.

For agent use, `pages/` is only useful when:

- the agent already knows the exact page number
- and the page-local markdown slice is materially better than using `document.md` plus indexes

That benefit has not been proven strong enough to justify default generation.

Current conclusion:

- `pages/` should be downgraded from default artifact to optional artifact

### 2. `README.generated.md` and `quality-summary.md` partially overlap

Current pattern in both bundle families:

- `README.generated.md` explains how to start
- `quality-summary.md` repeats bundle identity plus alert/count summary

This creates two small entry files that both must be read first.

Current conclusion:

- there should likely be a single primary entrypoint file for agents
- the split between `README.generated.md` and `quality-summary.md` is probably too fine-grained

### 3. `docling_bundle` still over-preserves table sidecars by default

Observed on the datasheet:

- each table is exported twice:
  - `tables/table_xxxx.csv`
  - `tables/table_xxxx.html`

This may be justified for some hard wide tables, but it doubles sidecar count immediately.

Current conclusion:

- `docling_bundle` should re-evaluate whether both formats are needed by default
- one format may become the default, with the other only opt-in

### 4. `manifest.json` is cleaner now, but can still shrink further

Recent cleanup removed the worst runtime/staging leakage, but the manifest still mixes:

- identity
- entrypoint references
- counts
- parser-specific bookkeeping

Current conclusion:

- the best agent-facing manifest should be a small stable entrypoint, not a wide export ledger

### Current bundle-layer judgment

Likely default keepers:

- one primary entry file (`ENTRY.md` / `index.md`)
- `manifest.json` (minimal)
- `alerts.json`
- `document.md`
- `document.json`
- one structured navigation/index layer
- one default table sidecar format
- visual assets (`figures/` or `artifacts/`)

Likely optional/off-by-default:

- `document.html`
- `pages/`
- secondary entry file if README/summary remain split
- duplicate table sidecar format
- extra runtime/debug layers beyond minimal evidence

### Stronger best-practice conclusion

Best practice is not:

- "export every representation that might someday help"

Best practice is:

- "export the smallest stable bundle that lets Codex / Claude Code read, navigate, verify, and know when to distrust the parse"

That implies:

1. parser internals may differ, but the agent-facing shell should converge where it improves the same consumer workflow
2. debug/runtime/cache/raw layers should move out of the final bundle by default
3. a bundle profile system is justified:
   - default: `agent-minimal`
   - optional: `agent-extended` / `debug`
4. `README.generated.md` and `quality-summary.md` should likely collapse into a single primary entry file

### Best-practice target shape from first principles

The final bundle should behave like a small local reference appliance for agents, not like a parser lab dump.

More appropriate default shape:

```text
<doc_id>/
  README.md
  manifest.json
  alerts.json
  document.md
  document.html
  document.json
  locator.index.jsonl
  tables.index.jsonl
  tables/
  assets/
```

Where:

- `README.md` is the only entrypoint file
- `manifest.json` is minimal and stable
- `locator.index.jsonl` is the preferred long-term single navigation layer
- `assets/` is the preferred long-term neutral visual asset directory name across parser families

Default removals / off-by-default artifacts:

- `pages/`
- `runtime/`
- `native/` / `raw/` / `cache/` leakage
- multiple competing entry files
- duplicate table sidecar formats unless proven necessary

## 2026-04-15 Regenerated Bundle Reality Check

After the latest reduction wave and clean reruns, the default bundle shape is materially cleaner:

- single `README.md`
- no default `pages/`
- no default runtime/native/cache layer inside final bundles
- unified visual asset directory `assets/`
- single default CSV table sidecar format

However, the regenerated bundles are still not at a final optimum.

### Current file-count / size reality

Current regenerated bundle sizes:

- `opendataloader_hybrid` datasheet: `5.2M`
- `opendataloader_hybrid` TRM: `53M`
- `docling_bundle` datasheet: `16M`
- `docling_bundle` TRM: `203M`

Breakdown shows the next major issue is no longer `pages/`; it is the visual asset layer:

- `odl-ds`: `assets` about `0.48M`
- `odl-trm`: `assets` about `0.58M`
- `doc-ds`: `assets` about `2.66M`
- `doc-trm`: `assets` about `48.3M`

### Revised image-policy conclusion

The project should preserve full extracted image evidence by default.

Reason:

- heuristic image filtering can misjudge what later becomes important engineering evidence
- timing diagrams, block diagrams, pin matrices, register visuals, and odd figure-tables are exactly the content most likely to be needed later
- for this project, information loss is a bigger risk than bundle size growth

So the right conclusion is:

- keep `assets/` complete by default
- do not apply heuristic image pruning in the final bundle
- accept larger bundle size as the cost of preserving visual evidence

### Refined keep / optional judgment

Likely default keepers:

- `README.md`
- `manifest.json`
- `alerts.json`
- `document.md`
- `document.json`
- `document.html` for now
- one navigation layer
- `tables.index.jsonl`
- `tables/*.csv`
- full `assets/`

Likely next optional candidates:

- extra derived navigation layers that duplicate existing ones
- redundant sidecar formats
- extra runtime/debug layers

## OpenDataLoader Hybrid First Real Run

The first real OpenDataLoader hybrid run on `esp32-s3_datasheet_en.pdf` has now completed.

### Environment facts

- Java 17 is available at the WSL system layer.
- OpenDataLoader runs in its own project overlay:
  - `opendataloader/.venv`
- The overlay now reuses the shared heavy AI base instead of reinstalling `torch`.
- This is the correct layering:
  - system Java
  - shared AI base for `torch`
  - project overlay for OpenDataLoader-specific Python packages

### Native output shape observed

For the ESP32-S3 datasheet, OpenDataLoader wrote:

- `esp32-s3_datasheet_en.json`
- `esp32-s3_datasheet_en.md`
- `esp32-s3_datasheet_en.html`
- `esp32-s3_datasheet_en_images/`

This is materially different from `docling_bundle`.

Key implication:

- OpenDataLoader native output is a flat per-document file set plus a suffixed image directory, not a pre-bundled document folder

### JSON schema reality from actual sample

Observed root keys:

- `file name`
- `number of pages`
- `author`
- `title`
- `creation date`
- `modification date`
- `kids`

Observed element keys:

- `id`
- `type`
- `page number`
- `bounding box`
- `content`
- `heading level`
- `level`
- font-related fields

Important correction:

- the actual element fields use spaced names like `page number` and `bounding box`
- any Codex-facing bundler must explicitly support those keys

### First-run hybrid behavior

The datasheet run reported:

- 87 pages total
- triage summary: `JAVA=18, BACKEND=69`

This is useful because it shows hybrid mode is not just a blind full reroute:

- some pages stay on the fast Java path
- harder pages go to the backend

### First bundler issues found and fixed

The first OpenDataLoader bundler draft had three real issues:

1. It did not understand spaced JSON field names.
2. It did not copy native `<stem>_images/` directories.
3. It could leave stale bundle files from a previous run in place.

Status:

- spaced metadata keys: fixed
- suffixed image directory support: fixed
- stale bundle cleanup: still needs one explicit cleanup pass or rebuild policy tightening

### Current Codex-facing OpenDataLoader bundle status

The generated bundle now includes:

- `README.generated.md`
- `quality-summary.md`
- `document.json`
- `document.md`
- `document.html`
- `elements.index.jsonl`
- `pages/`
- `figures/`
- `manifest.json`
- `alerts.json`

For the ESP32-S3 datasheet:

- `page_count = 87`
- `alerts = []`
- `elements.index.jsonl` now contains page numbers and bounding boxes

This means the first OpenDataLoader bundle is now minimally valid for Codex evaluation.

## OpenDataLoader TRM Failure And Retry

The first `OpenDataLoader PDF hybrid` run on `esp32-s3_technical_reference_manual_en.pdf` did not complete successfully.

### Failure observed

- document: 1,531 pages
- triage summary: `JAVA=173, BACKEND=1,358`
- failure point: backend processing after reaching pages in the `995-1050` region
- exception:
  - `java.lang.IllegalArgumentException: Comparison method violates its general contract!`
  - thrown from `org.opendataloader.pdf.hybrid.DoclingSchemaTransformer.sortByReadingOrder(...)`

### What this means

This is not just a timeout or an environment issue.

It is a real tool stability issue on a very large TRM under hybrid mode:

- the backend can process many windows successfully
- but the final transform/sort step can crash the whole run

### Response

The runner has now been changed to enable `--hybrid-fallback` by default.

Reason:

- for large manuals, a partial-quality fallback is better than a total run failure
- this matches the project goal of maximizing Codex-usable output, not parser purity

The current in-flight retry will tell us whether fallback is enough to make OpenDataLoader viable on large TRMs.

### Retry outcome

The fallback-enabled retry did complete successfully.

Observed behavior:

- the same backend sorting bug was triggered again
- `--hybrid-fallback` prevented total run failure
- OpenDataLoader fell back to Java processing for the affected backend pages
- final native outputs were written successfully

This means the current best-practice reading is:

- `hybrid` without fallback is not resilient enough for very large TRMs
- `hybrid + fallback` is currently the only credible OpenDataLoader setting for this class of manual

### TRM bundle facts

The resulting Codex-facing TRM bundle now reports:

- `page_count = 1531`
- `element_count = 30290`
- `table_count = 2467`
- `alert_count = 0`

It also now includes:

- page-level slices for all 1,531 pages
- `elements.index.jsonl`
- `tables.index.jsonl`
- `runtime/native/` with the original OpenDataLoader-native files for this document only

### Structural conclusion

This confirms a more precise statement about OpenDataLoader:

- it is relatively light on GPU compared with a fully model-driven pipeline
- it is often fast
- but on very large TRMs it currently needs fallback enabled to be operationally reliable

So its current best practice is not:

- bare hybrid

but:

- `docling-fast hybrid + cuda + hybrid-fallback`

## Preliminary Datasheet Comparison: OpenDataLoader vs Current Docling Bundle

This is an early comparison on `esp32-s3_datasheet_en.pdf`, not the final verdict.

### What OpenDataLoader is already better at

For the datasheet bundle:

- `elements.index.jsonl` exposes page-aware element records with actual bounding boxes.
- `pages/page_0027.md` shows the full page as positioned text fragments plus the table image.
- the JSON tree already contains structured `table` elements for many pages.
- the current OpenDataLoader bundler now exports 68 CSV table sidecars from those structured tables.

This is a real advantage over the current `docling_bundle` layout when Codex needs:

- exact page-local element inspection
- element-level spatial metadata
- structured table exports from the native parser tree

### What is still weaker or ambiguous

`Table 2-9. Peripheral Pin Assignment` is not represented as a native `table` element in OpenDataLoader.

Instead, on page 27 it appears as:

- one heading
- one large image
- many paragraph elements with bounding boxes for apparent cell text

That means:

- OpenDataLoader can still expose the evidence on the page
- but it does not automatically yield a neat CSV sidecar for this specific hard table

By contrast, the current `docling_bundle` output also does not provide a clean sidecar for this exact page, but its reading layer already has a stronger established pattern for sidecar-linked tables on pages where Docling does structure them.

### Current takeaway

The current early evidence suggests:

- OpenDataLoader is stronger on page-local spatial evidence
- OpenDataLoader's structured tables are highly valuable when present
- OpenDataLoader still has hard-table failure modes where the best artifact is page evidence rather than a table sidecar
- `docling_bundle` remains stronger on the current human-readable bundle conventions

So the likely comparison direction is not:

- "one parser always wins on every artifact"

but:

- "which bundle helps Codex recover from each parser's failure modes more effectively"

After the TRM run, the more specific comparison is:

- OpenDataLoader currently looks stronger on large-scale page/bbox/table evidence volume
- Docling still has the more mature current reading bundle and table-sidecar conventions
- OpenDataLoader is faster/lighter on GPU, but presently less stable without explicit fallback on huge manuals

## `docling_bundle` Rename Outcome

The rename has now been executed.

Old name:

- `docling_batch`

New name:

- `docling_bundle`

Reason:

- the package is now primarily a Docling-specific bundle builder
- the new output tree is explicitly Codex-facing
- the old `batch` label no longer describes the main value of the code well

What changed:

- Python package directory renamed to `docling_bundle/`
- CLI entry moved to `python -m docling_bundle convert`
- output root moved to `manuals/processed/docling_bundle/<doc_id>/`
- active docs, tests, and instructions updated to the new name

What did not change:

- some historical plan/spec/architecture filenames still contain `docling-batch`
- those are retained as historical records, not active product naming

## Final Comparison Snapshot

At the end of this execution round, both active candidates have been exercised on the fixed Espressif samples and packaged into Codex-facing bundles.

### OpenDataLoader hybrid bundle

Strengths:

- faster initial throughput
- lighter apparent GPU dependence because Java handles part of the pipeline
- element-level page and bounding-box metadata
- very large structured table yield
- strong page-local forensic view via `elements.index.jsonl` and `pages/`

Confirmed bundle facts:

- datasheet: `87` pages, `3187` elements, `68` tables, `0` alerts
- TRM: `1531` pages, `30290` elements, `2467` tables, `0` alerts

Weaknesses:

- large TRMs are not stable enough without `--hybrid-fallback`
- some hard tables still degrade into `image + positioned text` rather than clean table exports
- page views are information-rich but less pleasant for quick reading

### `docling_bundle` bundle

Strengths:

- cleaner reading experience in `document.md` and `pages/`
- explicit table sidecar links embedded near reading context
- explicit quality signaling through alert files and summaries
- stable large-manual execution with window cache and no parser crash in this round

Confirmed bundle facts:

- datasheet: `87` pages, `71` tables, `1` alert
- TRM: `1531` pages, `668` tables, `10` alerts

Weaknesses:

- heavier runtime profile on big manuals
- much less spatial metadata than OpenDataLoader
- lower structured-table coverage
- figure-like tables can still become empty or weak sidecars

### Codex verdict

If forced to choose one parser/output family today:

- **best evidence extractor:** `OpenDataLoader PDF hybrid` with `--device cuda --hybrid-fallback`
- **best reading bundle:** improved `docling_bundle`

If forced to choose one **overall Codex-facing bundle** today:

- `docling_bundle` is still slightly better for direct reading and verification workflow because the bundle is calmer and more self-explanatory
- `OpenDataLoader` is stronger when the task depends on page-local spatial evidence, bbox-aware debugging, or very high table coverage

So the practical decision is:

- keep both for now
- treat `OpenDataLoader hybrid` as the stronger extraction/evidence path
- treat `docling_bundle` as the stronger current reading/verifier path
- keep `docling_bundle` as the current Docling-side product name while the broader parser comparison continues

## 2026-04-15 Final Bundle Optimization Wave

This wave focused on low-risk bundle improvements that directly help Codex.

### OpenDataLoader improvements proven useful

1. `runtime/report.json`
   - surfaces triage summary
   - surfaces fallback/backend-failure state
   - turns hidden runner behavior into explicit bundle metadata
2. image-backed table alerting
   - pages like `Table 2-9. Peripheral Pin Assignment` now produce an explicit alert instead of failing silently

These help because they improve Codex judgment without distorting native evidence.

### Docling improvements proven useful

1. alert page references in `quality-summary.md`
   - the summary now points directly to the page that needs inspection
   - captions/details are surfaced inline

This shortens the path from:

- "there is a quality warning"

to:

- "open page 27 now"

### Current stopping point

The next likely improvements are more invasive and less predictable:

- reconstructing image-backed hard tables in OpenDataLoader
- adding more aggressive Docling-side prioritization heuristics

So the current judgment is:

- keep this optimization wave
- only continue with a larger wave if we accept more complexity and more uncertain returns

## Diminishing Returns Assessment

For the current repository goal, we are now in diminishing-returns territory.

That means:

- the current outputs are already good enough for real Codex use
- further parser-output work is still possible
- but the next changes are no longer obvious improvements

The remaining likely work items are things like:

- reconstructing image-backed hard tables in OpenDataLoader
- adding more aggressive Docling-side alert routing or prioritization
- building a more formal comparison harness

All of these may help, but none of them is a clear "must-have before using the system".

So the current recommendation is:

- treat the current parser/bundle state as sufficiently mature
- only reopen parser-output engineering when a new manual class or a concrete failure justifies it

## Project Structure Clarification

The project now has a current structure document:

- `docs/architecture/2026-04-15-project-structure.md`

This is useful because the repository now has a clear split between:

- parser overlay environments
- parser-side bundle builders
- raw PDFs
- final processed bundles
- temporary staging data
- current docs vs superseded docs

That structure is now explicit instead of being inferred from scattered notes.

## Deferred

- OpenDataLoader + LlamaIndex
- Dify
- AnythingLLM
- Kotaemon
- Open WebUI
- LiteParse
- PyMuPDF4LLM
- MarkItDown
- PaperFlow
- PaddleOCR-VL / PP-StructureV3
- Marker
- MinerU
- HURIDOCS
- Markdrop / pdfmd
- RAGFlow
- Unstructured
- paid/remote parser APIs

## References

- OpenDataLoader PDF: https://github.com/opendataloader-project/opendataloader-pdf
- OpenDataLoader PDF LangChain integration: https://docs.langchain.com/oss/python/integrations/document_loaders/opendataloader_pdf
- OpenDataLoader RAG integration guide: https://opendataloader.org/docs/rag-integration
- OpenDataLoader Hybrid Mode: https://opendataloader.org/docs/hybrid-mode
- Docling LlamaIndex integration: https://docling-project.github.io/docling/integrations/llamaindex/
- LangChain Docling loader: https://docs.langchain.com/oss/python/integrations/document_loaders/docling

## 2026-04-15 Documentation Noise Cleanup

Active documentation had started to drift in two ways:

1. some files still described deleted bundle layers such as `README.generated.md`, `quality-summary.md`, `pages/`, and `runtime/native`
2. some active status/roadmap docs still described already-completed cleanup work as if it were still the next plan

The cleanup rule for this repository should now be:

- active docs describe only the current production bundle shape
- deleted structures are mentioned only when strictly necessary to explain a current design rule
- historical reports that still teach obsolete structure should be removed from the active doc set instead of kept around as quasi-current references

Concrete cleanup completed:

- removed `docs/architecture/2026-04-15-executive-project-report.md`
- updated `docs/README.md` to keep the active doc set explicit
- corrected current facts in `docs/architecture/2026-04-15-parser-status-and-next-steps.md`
- rewrote the roadmap so it reflects the post-reduction baseline rather than re-planning already-finished cleanup
- corrected `docs/architecture/2026-04-15-project-structure.md` wording and link text
- corrected `docs/architecture/2026-04-12-docling-embedded-manual-processing.md` to the real processed path and current downstream framing

Current verified facts used for the cleanup:

- `opendataloader_hybrid` datasheet alerts: `1`
- `opendataloader_hybrid` TRM alerts: `0`
- `docling_bundle` datasheet alerts: `1`
- `docling_bundle` TRM alerts: `9`
- current local bundle sizes are approximately `4.7M`, `40.4M`, `15.2M`, and `197.3M`

Verification after cleanup:

- grep confirmed no active doc still presents deleted bundle layers as current defaults
- the structural test suite still passes

## 2026-04-18 Project Reassessment (Phase 38-41 status review)

### Stated vs actual state

`task_plan.md` claims Phase 38 (Navigation Layer Enhancement) is complete. Deep inspection shows:

| Item | Claim | Reality |
|------|-------|---------|
| `patterns.py` extraction | complete | done, file present, uncommitted |
| `infer_heading_level()` | complete | code exists in `indexing.py`, tested |
| `build_toc()` | complete | code exists in `indexing.py`, wired into `converter.py` L460-461 |
| `build_pages_index()` | complete | code exists, wired into `converter.py` L463-464 |
| `flag_suspicious_sections()` | complete | code exists, wired L440 |
| `document_index` table markers | complete | present in existing `tables.index.jsonl` |
| Bundles regenerated | implicit | NO — existing bundles are stale, lack `toc.json` / `pages.index.jsonl`, still show `heading_level: 1` for every section |
| Code committed | implicit | NO — 8 files dirty, `patterns.py` untracked, `AUDIT_REPORT.md` untracked |

The code is genuinely done but the project has not closed the loop with a clean regeneration + commit.

### Remaining original audit items (not yet addressed)

| Area | Problem | Status |
|------|---------|--------|
| ODL Markdown | figure-text fragments (e.g. "External", "Switch", "Baseband" as loose paragraphs) | confirmed still present in datasheet bundle |
| ODL Manifest | `page_numbers` stored as full 87-element (or 1531-element) array | confirmed still present |
| Docling assets | hash-based filenames `image_NNNNNN_<64-hex>.png` with no page/semantic info | confirmed |
| Code quality | `converter.py` still 531 lines (was 520) doing 9 jobs | unchanged |
| Code quality | ODL 3-layer redundant asset-lookup loop | unchanged |
| Code quality | ODL key-variant handling scattered across `_normalize_page` / `_normalize_bbox` / `_element_text` | unchanged |
| Tests | no small-PDF integration test | unchanged |
| Tests | `cli.py`/`__main__.py` in both tools have zero coverage | unchanged |
| Tests | no error-path or boundary-condition coverage | unchanged |

### New findings from this reassessment

Additional AI-consumer gaps not covered in the original audit:

1. **Bundle link integrity is not a checked invariant.** Nothing verifies every `![...](assets/...)` reference in `document.md` resolves to a bundle-local file. The earlier ODL bug where `document.md` pointed at `*_images/` paths outside the bundle could silently regress.
2. **Alerts are structurally complete but not actionable enough.** `table_caption_followed_by_image_without_sidecar p.27: Table 2-9. Peripheral Pin Assignment` tells me *what* is wrong, but to recover I still have to manually scan `document.md` for p.27 to locate the image. If the alert carried `fallback_image: assets/image_0027_xxxx.png`, I would be one hop away from the truth.
3. **Cross-references are not extracted.** Chip manuals are dense with "See Section 4.1.3.5" / "Refer to Table 2-5" / "Figure 3-1". Today those are plain text. Making them queryable (`cross_refs.jsonl`) would convert navigation from O(text search) to O(index lookup).
4. **Register tables and pin-assignment tables have no semantic marker.** For embedded work these are the single highest-value table kinds. A cheap heuristic on CSV column headers (`Bit Field`, `Reset`, `Attribute` for registers; `Pin Name`, `GPIO`, `Function` for pinouts) could mark each table with `kind: register | pinout | generic` in `tables.index.jsonl` and cut my table-scanning by a lot.
5. **README is structural but not content-rich.** It lists file names but not "here are the 5 most important tables", "here is the chapter outline", "here are the first 3 alerts with next-step hints". I have to open the navigation files to find those — one more hop than necessary.
6. **No MCP surface.** Every bundle lookup is me reading a file. A thin MCP server (`lookup_page`, `lookup_table`, `find_register`, `follow_xref`) would let the harness call structured retrieval with no model-side parsing cost. This is an outcome-multiplier, not a correctness fix.

### Re-prioritization rationale

The original audit's Phase 1-4 ordering is still correct, but a missing bracket phase must come first: **regenerate + validate + commit what is already done.** Without that, Phase 39-41 would stack more code on top of unverified Phase 38 behaviour, and we keep discovering cosmetic issues (heading_level=1, missing `toc.json`) that only exist because the bundles were never re-run.

The new AI-consumer findings above map to a new Phase F that sits above "long-term exploration": they are not speculative (they are directly motivated by my own daily use) but they do add real behaviour, so they should follow the refactor/test hardening phase.

## 2026-04-18 Fresh Docling Datasheet Bundle Inspection

重跑后的 `manuals/processed/docling_bundle/esp32-s3-datasheet-en/` 实测结果：

### 成功落地的 Phase 38 成果

| 产物 | 实测 |
|---|---|
| `toc.json` | 212 条，level 分布 `{1: 111, 2: 26, 3: 23, 4: 52}` |
| `sections.jsonl` | 141 条，level 分布 `{1: 46, 2: 22, 3: 23, 4: 50}` |
| 异常 section 标注 | `"Note:" spans 54/87 pages (62%)` 被抓到，只有 1 条 |
| `pages.index.jsonl` | `p.27` 反查到两个 chunk + alert kind |
| README | 引用了新文件，alert 直出 |
| 图片引用完整性 | `document.md` 里 85 个引用全部在 `assets/` 中存在 |

### Phase 38 做完仍然严重影响查阅的新问题

#### Problem A: TOC 的 L1 分类太粗，产生大量噪音

111 条 `level: 1` 里只有约 9 条是真正的章节（1 / 2 / 3 / 4 + 章节级 Revision / Disclaimer）。其余都是误分类：

- `ESP32-S3 Series` / `Datasheet Version 2.2` / `Including:` — 封面文字
- `Product Overview` / `Power consumption` / `ESP32-S3 Functional Block Diagram` — 封面段落标题
- `Contents` / `List of T ables` / `List of Figures` — 目录前言
- `Cont'd from previous page` — 表格续页标记出现 5 次
- `Feature List` — 同名重复出现 3 次，彼此无区分
- `Note:` — 早前审计就标的伪章节
- `Table 2-9. Peripheral Pin Assignment` — 表格 caption 被当 heading

**根因**：`build_toc()` 里只做了 `"heading" in label_str.lower() or label_str == "section_header"` 判断，再用数字前缀推层级。没有应用 `sections.py` 里已有的 `NOISY_SECTION_IDS` / `NOISY_TEXT_PATTERNS` 过滤，也没有吸收 `flag_suspicious_sections` 的标记。

**影响**：我要从 212 条里肉眼挑真正的 9 条章节，TOC 反而增加阅读负担。

#### Problem B: 真·章节出现但缺失了后半部分

datasheet 实际章节应该有 5/6/7/8/9，但 TOC 里只看到 `1 / 2 / 3 / 4`，后续章节（Electrical Characteristics / Package / Part Number / Ordering / Revision History）在 L1 里没有出现对应的 `N Chapter Name` 形式——它们要么被 Docling 识别为其他 label，要么被 noise 淹没。

需要在 `build_toc` 里识别 "数字打头+空格+大写" 这类章节强模式，强行 promote 到 L1 并标 `is_chapter`。

#### Problem C: 表格 caption 覆盖率 54/71 (76%)，但排除 `document_index` 后是 48/65 (74%)

缺失 caption 的 17 张大多是 "cont'd from previous page" 续页表，这些表可以从前一张表继承 caption 并标记 `continuation_of: <table_id>`。

#### Problem D: 交叉引用密度实测

`document.md` 实测：
- `See Section X.Y` 24 次（9 个不同目标，最常见 `4.1.3.5`）
- `See Table X-Y` 1 次
- `See Figure X-Y` 3 次
- `Refer to Section X.Y` 2 次

对 87 页 datasheet，30 个交叉引用是真实、可索引、可直接跳转的导航边。输出 `cross_refs.jsonl` 的收益是把我从"全文扫描"降到"查一个 jsonl"。

#### Problem E: 图片文件名仍是无语义哈希

现状：`assets/image_000025_0430387ca41b0c87fce...png`

当 alert 提到 "p.27 Table 2-9 没有 sidecar，有图片替代" 时，我需要：
1. 打开 `document.md` 搜 p.27 附近的 `![Image](assets/...)`
2. 把那条引用 copy 出来
3. 去 `assets/` 目录核对

如果文件名是 `p027_figure_001.png`，我直接跳到 p.27 对应文件即可。

#### Problem F: 表格 sidecar 目前只有 CSV，寄存器表 / 引脚表无语义标注

所有 65 条正式表格在 `tables.index.jsonl` 里都是平等的。但嵌入式开发最高频查阅的：

- **寄存器表**（CSV header 含 `Bit`/`Reset`/`Attribute`/`Field`）
- **引脚表**（CSV header 含 `Pin`/`GPIO`/`Function`）
- **电气特性表**（CSV header 含 `Parameter`/`Min`/`Typ`/`Max`/`Unit`）

给 `tables.index.jsonl` 增加 `kind` 字段让我可以 `grep '"kind":"register"'` 直接筛出我关心的类型。

### Docling-only 聚焦后的优先级（取代旧 Phase 40-44）

1. **TOC 去噪与补完**（Problem A + B）— 直接决定导航可用性
2. **表格 caption 续页继承**（Problem C）— 提升查表命中率
3. **交叉引用抽取 `cross_refs.jsonl`**（Problem D）— 全新能力，开销低
4. **表格 `kind` 启发式标注**（Problem F）— 嵌入式场景最高频
5. **图片语义重命名 + `assets.index.jsonl`**（Problem E）— 降低 alert→源文件跳转成本
6. **代码质量清理**（converter.py 拆分、O(n²) 消除）
7. **测试补强**（端到端集成 / CLI / 错误路径 / bundle 完整性）

## 2026-04-18 Phase 39 Implementation Results

### Commit `32eae51` baseline (Phase 38) vs after Phase 39

| 指标 | Phase 38 | Phase 39 | 变化 |
|---|---|---|---|
| TOC 总条目 | 212 | 151 | -29% |
| TOC L1 条目 | 111 | 50 | -55% |
| TOC L1 真章节比例 | 7/111 = 6% | 7/50 = 14%（+ `is_chapter` 精确筛选 100%） | 大幅改善 |
| "Feature List" 重复数 | 29 | 0 | 清理 |
| "Pin Assignment" 重复数 | 15 | 0 | 清理 |
| "Note:" 重复数 | 8 | 0 | 清理 |
| "Cont'd from previous page" 数 | 5 | 0 | 清理 |
| 表格 caption 误为 heading | 1 ("Table 2-9...") | 0 | 清理 |
| 测试数 | 74 | 83 | +9 |

### 实测验证 AI-consumer 体验

用 `jq '.[] | select(.is_chapter)' toc.json` 立刻返回 7 条：

```
p.13: 1 ESP32-S3 Series Comparison
p.15: 2 Pins
p.32: 3 Boot Configurations
p.36: 4 Functional Description
p.64: 5 Electrical Characteristics
p.70: 6 RF Characteristics
p.77: 7 Packaging
```

这就是 datasheet 的真实章节目录。任务"哪些章节存在"从 "grep 212 条"降到"jq 一行"。

### 剩余弱点（作为 Phase 40+ 证据）

- 非章节 L1 仍有 50 条噪音（封面文字、无编号的子段标题），但可通过 `is_chapter` 过滤一键跳过
- `suspicious` 在本 datasheet 无可见触发；需要在其他手册（典型场景：heading 被误识为 "Figure 1-X"）才能观察链路
- 表格 caption 仍有 17/65 缺失（Phase 40 要处理）
