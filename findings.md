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
