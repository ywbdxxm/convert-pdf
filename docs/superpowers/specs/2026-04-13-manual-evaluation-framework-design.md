# Manual Evaluation Framework Design

Date: 2026-04-13

## Goal

Build a framework for comparing embedded-manual processing approaches without prematurely committing to a custom pipeline.

The framework must answer:

- What is the best way to use Docling itself, beyond the current `docling_batch` wrapper?
- Which parts of the current workflow are already handled better by existing tools?
- Which output shape actually helps AI/human lookup of chip manuals?
- Which tool should become the mainline after evidence-based A/B testing?

The first implementation must not add a new RAG stack, install heavy tools, or extend `docling_batch` behavior. It should create the framework for comparing tools and preserving evidence.

## Non-Goals

- Do not build a new universal PDF processing pipeline.
- Do not force every tool into `manuals/processed/<doc_id>`.
- Do not implement embeddings, vector search, re-ranking, or chat UI in this phase.
- Do not add more heuristics to `docling_batch`.
- Do not delete existing processed outputs until replacements are proven.
- Do not install Marker, MinerU, RAGFlow, Kotaemon, or other heavy tools in the framework skeleton phase.

## First-Principles Requirements

The project-specific value is not the converter implementation. The value is the evidence discipline for embedded development.

Every candidate tool should be judged by whether it helps answer manual questions with:

- page-level citation
- traceability to original PDF
- inspectable table values
- inspectable figures or page images for diagrams
- visible parser uncertainty or failure modes
- low maintenance burden

For register values, bit definitions, pin mappings, timing limits, and electrical characteristics, the final authority remains the original PDF.

## Current Baseline

The current `docling_batch` pipeline is a useful baseline, but not the architecture standard.

It currently provides:

- Docling PDF conversion through `DocumentConverter`
- JSON, Markdown, and HTML exports
- Docling `HybridChunker` records
- custom `chunks.jsonl` and `sections.jsonl`
- custom table CSV/HTML sidecars
- custom Markdown table sidecar links
- custom `alerts.json`
- optional custom window cache
- custom manifest and run summary files

This baseline should be frozen for comparison. It should not receive new features unless A/B testing proves a specific retention need.

## Docling Best-Practice Baselines

Docling should be evaluated in multiple native-first modes, not only through `docling_batch`.

### `docling-cli-native`

Purpose: evaluate Docling as an end-user CLI tool with minimal local code.

Use Docling CLI capabilities:

- convert files/directories directly
- output JSON, Markdown, HTML, and other native formats
- use referenced image export
- disable OCR for digital manuals by default
- enable GPU acceleration when available
- enable table extraction
- optionally enable profiling and debug visualization for hard pages

Expected output:

```text
manuals/evaluations/<run_id>/docling-cli-native/<doc_id>/raw/
```

The raw directory should contain Docling CLI outputs as-is. No forced reshaping into the current `manuals/processed/<doc_id>` layout.

### `docling-api-native`

Purpose: evaluate a minimal Python wrapper around Docling APIs without custom product behavior.

Allowed Docling APIs:

- `DocumentConverter.convert` / `convert_all`
- `DoclingDocument.save_as_json`
- `DoclingDocument.save_as_markdown`
- `DoclingDocument.save_as_html`
- `TableItem.export_to_dataframe`
- `TableItem.export_to_html`
- `HybridChunker`
- visual grounding or page-image APIs if needed for hard pages

Not allowed in this baseline:

- custom caption recovery
- custom table sidecar injection into Markdown
- custom alert heuristics
- custom window cache
- custom image filtering
- custom RAG/search layer

This isolates what Docling itself gives us.

### `docling-api-debug`

Purpose: inspect hard pages and determine whether Docling native debug/visual outputs already expose the information we need.

Use only for known problematic pages:

- ESP32-S3 peripheral pin assignment table
- pages with empty table sidecars in the current baseline
- formula-heavy pages
- figure/timing-diagram-heavy pages

This mode should not become the default bulk conversion mode.

### `docling-current-bundle`

Purpose: preserve the current `docling_batch` output as a historical baseline.

It should be copied or referenced into evaluation runs as one candidate, not treated as the desired schema.

## Other Candidate Tools

The framework should be tool-neutral. Initial candidates:

### Marker

Evaluate for:

- Markdown, JSON, HTML, and chunk output
- image extraction
- table handling
- optional table-specific conversion and LLM correction
- whether it handles wide embedded tables better than Docling

### MinerU

Evaluate for:

- Markdown/JSON output
- table HTML output
- image extraction
- long-document behavior
- WebUI/API usefulness
- whether its long-document pipeline reduces the need for our window cache

### RAGFlow

Evaluate as an application-level RAG tool, not just a converter.

Evaluate for:

- Docling/MinerU parser integration
- citation quality
- chunk visualization
- table-heavy answer quality
- re-ranking and multi-recall usefulness
- deployment cost

### Kotaemon

Evaluate as a lighter document-chat UI with Docling integration.

Evaluate for:

- quick local document chat
- source chunk visibility
- page citation quality
- ease of use compared with RAGFlow

### PyMuPDF4LLM

Evaluate as a lightweight digital-PDF baseline.

Evaluate for:

- speed
- Markdown quality
- page chunk quality
- whether it is sufficient for simple datasheets

### Unstructured

Evaluate as metadata-rich ingestion.

Evaluate for:

- typed elements
- page number metadata
- table HTML metadata
- coordinates
- whether its element model gives a better normalized evidence layer

## Directory Layout

Keep immutable sample PDFs under:

```text
manuals/raw/<vendor>/<chip>/<manual>.pdf
```

Create evaluation runs under:

```text
manuals/evaluations/<run_id>/
```

Each tool writes:

```text
manuals/evaluations/<run_id>/<tool>/<doc_id>/
  raw/
  normalized/
    manifest.json
    evidence.jsonl
  scorecard.md
```

Rules:

- `raw/` preserves native tool output.
- `normalized/` contains only the minimal comparison layer.
- `scorecard.md` records human/AI evaluation against fixed questions.
- Do not overwrite raw outputs from a previous run.
- Do not force native outputs into the current `manuals/processed/<doc_id>` structure.

## Minimal Evidence Schema

Use JSON Lines for normalized evidence.

Required fields:

```json
{
  "doc_id": "esp32-s3-datasheet-en",
  "tool": "docling-cli-native",
  "source_pdf_path": "manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf",
  "source_pdf_sha256": "...",
  "evidence_id": "docling-cli-native:esp32-s3-datasheet-en:000001",
  "evidence_type": "text",
  "page_start": 27,
  "page_end": 27,
  "heading_path": ["Pin Definition"],
  "text": "...",
  "native_ref": "raw/document.md",
  "table_ref": null,
  "image_ref": null,
  "risk_flags": []
}
```

Allowed `evidence_type` values:

- `text`
- `table`
- `image`
- `page`
- `alert`
- `metadata`

Rules:

- `native_ref` must point back to the raw tool output.
- `page_start` / `page_end` should be null only when the tool cannot provide page provenance.
- Do not hide missing provenance. Missing page numbers are a scorecard penalty.
- `risk_flags` should record parser uncertainty when available.

## Normalized Manifest Schema

Each tool/doc pair writes:

```json
{
  "run_id": "20260413T000000Z",
  "tool": "docling-cli-native",
  "tool_version": "...",
  "doc_id": "esp32-s3-datasheet-en",
  "source_pdf_path": "manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf",
  "source_pdf_sha256": "...",
  "raw_output_dir": "raw",
  "evidence_path": "normalized/evidence.jsonl",
  "status": "success",
  "errors": [],
  "notes": []
}
```

The manifest is not a replacement for native tool metadata. It is only an evaluation index.

## Scorecard

Each candidate should be scored against fixed questions.

Suggested score dimensions:

- `page_citation`: can it identify the correct source page?
- `text_recall`: does it retrieve the relevant prose?
- `table_recoverability`: can table values be inspected?
- `visual_traceability`: can diagrams/images be located?
- `risk_visibility`: does it expose parser uncertainty or failure?
- `answer_usefulness`: does it help answer the embedded question?
- `setup_cost`: how hard is the tool to install/run?
- `runtime_cost`: time, GPU/CPU, memory, disk
- `maintenance_cost`: how much custom code remains?

Use a simple 0-3 scale:

- `0`: fails or unavailable
- `1`: partial/manual workaround required
- `2`: usable with caveats
- `3`: strong

## Initial Evaluation Questions

Use the same questions for all tools.

### ESP32-S3 Datasheet

- Locate and inspect `Table 2-9. Peripheral Pin Assignment`.
- Find a GPIO/pin mux fact and cite the page.
- Find an electrical characteristic table value and cite the page.

### STM32H743VI Datasheet

- Locate a table-heavy pin/electrical section.
- Verify whether table captions and page ranges are recoverable.
- Check if wide tables are easier to inspect than in the current Docling baseline.

### ESP32-S3 Technical Reference Manual

- Locate an I2C register summary.
- Locate a UART register description.
- Find a formula/figure-heavy section.
- Check pages previously associated with empty sidecars or parser alerts.

## Framework Commands

The first implementation should provide lightweight commands only.

Suggested command names:

```sh
python -m manual_eval init-run --name docling-native-20260413
python -m manual_eval run-docling-cli --run <run_id> --input <pdf>
python -m manual_eval run-docling-api --run <run_id> --input <pdf>
python -m manual_eval import-current-baseline --run <run_id> --doc-dir manuals/processed/<doc_id>
python -m manual_eval normalize --run <run_id> --tool <tool> --doc-id <doc_id>
python -m manual_eval scorecard --run <run_id> --tool <tool> --doc-id <doc_id>
```

Phase 1 may implement only:

- directory creation
- manifest template writing
- scorecard template writing
- current baseline import
- Docling CLI/API run definitions

It does not need to run Marker/MinerU/RAGFlow yet.

## Error Handling

- Every tool run must write a manifest, even on failure.
- Raw tool stderr/stdout should be saved under `raw/` or a run log.
- Failed tools should still get a scorecard marked as failed.
- Normalization should fail explicitly if page provenance is unavailable, not silently invent pages.
- Tool installation failures should be recorded in the run-level notes, not hidden by fallback behavior.

## Testing Strategy

Unit tests:

- run ID creation
- output path planning
- manifest template writing
- evidence JSONL validation
- scorecard template generation
- current baseline import path validation

Integration tests:

- run a tiny fixture through Docling API if environment is available
- otherwise test adapters with recorded raw fixture snippets

No heavy external tool tests in the first implementation.

## Migration Strategy

Keep existing:

- `docling_batch/`
- `manuals/processed/`
- current tests
- current architecture docs

Add new framework alongside it:

- `manual_eval/`
- `criteria/`
- `manuals/evaluations/`

After A/B results:

- freeze `docling_batch` permanently if external tools are better
- shrink `docling_batch` into a thin Docling adapter if useful
- remove only after scorecards prove it is redundant

## Open Questions

- Should the first implementation include actual Docling CLI execution, or only run definitions and templates?
- Should normalized evidence include bounding boxes immediately, or defer until a tool proves bbox quality useful?
- Should scorecards be filled manually first, or should we add helper scripts to search evidence?
- Should RAGFlow/Kotaemon be evaluated before Marker/MinerU, or only after converter quality is settled?

## Recommendation

Start with a conservative framework skeleton:

- keep `docling_batch` frozen
- add `manual_eval` as evaluation scaffolding
- define Docling CLI/API native baselines
- create scorecard templates
- preserve raw outputs
- normalize only the smallest evidence layer

This keeps the project from growing another bespoke conversion pipeline while still letting us test whether Docling native usage, existing tools, or complete RAG software perform better for embedded manuals.
