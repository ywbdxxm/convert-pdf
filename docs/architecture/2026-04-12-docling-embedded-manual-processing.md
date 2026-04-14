# Docling Embedded Manual Processing Architecture

Date: 2026-04-12

## Purpose

This repository is not trying to build a generic PDF-to-Markdown toy.

The concrete goal is to convert chip datasheets, technical reference manuals, application notes, and similar embedded-development PDFs into assets that an AI assistant can read, search, cite, and verify while helping with firmware and driver work.

The design target is therefore:

- Preserve the original PDF as the final authority.
- Use Docling JSON as the canonical machine-readable parse.
- Keep a readable Markdown/HTML copy for human and AI inspection.
- Build page-aware retrieval indexes for fast lookup.
- Export table sidecars for electrical tables, register summaries, pin maps, and timing data.
- Record quality alerts instead of silently hiding Docling limitations.
- Keep the pipeline framework-independent so later agent tools or other downstream consumers can use the outputs without forcing a specific stack today.

## Design Principles

### First principle: the PDF remains authoritative

PDF conversion is lossy. Even a good parser can misread wide tables, register bit diagrams, equations, figure captions, page furniture, or dense matrix layouts.

For embedded development, a wrong register bit, pin function, timing limit, or electrical characteristic can produce real engineering errors. The original PDF must remain available and cited by page. The processed assets exist to accelerate lookup and make cross-checking easier, not to replace the source PDF.

### Second principle: canonical structure beats Markdown-only processing

Markdown is useful, but it is not the canonical artifact. Our canonical artifact is `document.json`, the Docling document export.

The current pipeline is:

```text
raw PDF
  -> Docling DocumentConverter
  -> DoclingDocument JSON
  -> Markdown / HTML reading copies
  -> Docling HybridChunker records
  -> sections/chunks/table sidecars/alerts
```

This is aligned with Docling's own direction: keep a structured document representation, then derive downstream reading and retrieval artifacts.

### Third principle: retrieval and reading are different layers

`document.md` should stay close to the parsed document. It may retain some page furniture and imperfect formatting because it is the full reading copy.

`chunks.jsonl` and `sections.jsonl` are retrieval layers. They are allowed to be cleaner and more search-oriented.

`tables/*.csv` are verification layers. When a value matters, use table sidecars and the original PDF page to cross-check.

### Fourth principle: cache is optional resilience, not default acceleration

Most datasheets and manuals are processed once. For those, default full-document conversion is simpler and avoids extra control flow.

Window cache is opt-in:

- Default: no window cache, full-document conversion.
- Use `--enable-window-cache --cache-window-size N` for very large manuals, unstable long runs, or repeated conversion experiments.

The cache exists to avoid losing all progress on large PDFs, not to make the first run faster.

### Fifth principle: do not overfit Docling limitations

Some layouts are simply hard for Docling's standard pipeline:

- ultra-wide pin/alternate-function matrices
- register bit diagrams rendered as figures
- formulas that cannot be serialized cleanly to MathML
- figure-like objects misclassified as tables
- empty table sidecars from parsed table items that have no usable cells

The project should not keep piling on fragile heuristics. When a limitation is clear, record it in `alerts.json` and use those alert pages for later A/B comparison with Marker, MinerU, OpenDataLoader PDF, or other tools.

## Repository Layout

The intended manual layout is:

```text
manuals/
  raw/
    <vendor>/<chip>/<manual>.pdf
  processed/
    docling_bundle/
      <doc_id>/
        README.md
        manifest.json
        alerts.json
        document.md
        document.json
        document.html
        sections.jsonl
        chunks.jsonl
        tables.index.jsonl
        assets/
        tables/
```

Examples currently used:

```text
manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf
manuals/raw/espressif/esp32s3/esp32-s3_technical_reference_manual_en.pdf
manuals/raw/st/stm32h7/stm32h743vi.pdf
```

## Generated Artifacts

### `document.json`

Canonical Docling document export.

Use it when:

- downstream code needs the structured Docling representation
- a derived index needs to be regenerated
- Markdown is insufficient to understand document structure
- later derived analysis needs a richer source than plain Markdown

Do not edit this by hand.

### `document.md`

Main reading companion for AI and humans.

It contains:

- headings
- prose
- Markdown tables
- page break placeholders
- image links into `assets/`
- table sidecar links inserted after matched tables

It intentionally is not heavily cleaned. It can contain page furniture, broken words, or parser artifacts. Treat it as a readable parse, not as a certified source of truth.

### `document.html`

HTML reading companion.

Use it when:

- a wide table is painful in Markdown
- an image-heavy page needs easier visual inspection
- human review is more important than machine chunking

The current implementation exports Docling's HTML directly and keeps it as a companion artifact.

### `README.md`

Single entrypoint for agents.

It summarizes:

- document identity
- page/table/alert counts
- which files to open next
- which alerts deserve caution

### `manifest.json`

Document-level metadata and output manifest.

It records:

- document identity
- source PDF path
- page count
- processing status
- alert/table counts
- stable relative entry file names

Use `README.md` first, then `manifest.json` as the machine-readable entrypoint.

### `sections.jsonl`

Section navigation index.

Each record groups chunks by heading path and includes:

- `doc_id`
- `section_id`
- `heading_path`
- `page_start`
- `page_end`
- `chunk_count`
- `text_preview`
- related table records when page ranges overlap

Use it to answer "where in the manual is this topic?"

### `chunks.jsonl`

Retrieval index generated from Docling native chunking.

Each record includes:

- `doc_id`
- `chunk_id`
- `heading_path`
- `page_start`
- `page_end`
- `text`
- `contextualized_text`
- `citation`
- `table_like`
- related table records when page ranges overlap

Use it to find relevant passages quickly. For final engineering answers, cite the page and verify important values in the sidecar table or original PDF.

### `tables/*.csv`

Table sidecars.

Use them for:

- register summaries
- electrical characteristics
- timing limits
- pin maps
- peripheral feature tables
- long tables that are hard to read inside Markdown

The pipeline inserts table links into `document.md` where possible:

```text
Table sidecar: [CSV](tables/table_XXXX.csv) | `doc_id:table:XXXX`
```

If exact insertion fails, the table is listed in a `Table Sidecars Appendix` at the end of `document.md`.

### `assets/`

Image sidecars generated by Docling.

Use them for:

- block diagrams
- register bit diagrams
- timing diagrams
- flow diagrams
- wide visual tables that Docling did not structure as tables

The current project intentionally keeps images by default. Losing a real timing diagram or pin matrix is worse than retaining some low-value images.

### `alerts.json`

Quality alert file.

Current alert types:

- `table_caption_followed_by_image_without_sidecar`
- `empty_table_sidecar`

Use this before trusting a document's structured output. Alerts do not mean the conversion failed; they mean the AI or human should inspect the original page, image, or sidecar before relying on that content.

### Window Cache

Optional window cache now lives outside the final bundle under:

```text
tmp/docling_bundle-cache/<doc_id>/
```

This keeps runtime resilience separate from the final agent-facing artifact.

## How To Run

### Default for digital datasheets and manuals

Use this for most PDFs:

```sh
docling/.venv/bin/python -m docling_bundle convert \
  --input manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf \
  --output manuals/processed \
  --device cuda \
  --no-ocr
```

This keeps the pipeline simple:

- full-document conversion
- no OCR
- images referenced as sidecars in `assets/`
- CSV table sidecars exported
- no window cache

### Large manuals where you want resumability

Use this for very large manuals or long-running experiments:

```sh
docling/.venv/bin/python -m docling_bundle convert \
  --input manuals/raw/espressif/esp32s3/esp32-s3_technical_reference_manual_en.pdf \
  --output manuals/processed \
  --device cuda \
  --no-ocr \
  --enable-window-cache \
  --cache-window-size 250
```

This is not expected to speed up the first run. It is used so a failure after several hundred pages does not force a full restart.

### Scanned or image-heavy PDFs

Only enable OCR when the PDF actually needs it:

```sh
docling/.venv/bin/python -m docling_bundle convert \
  --input manuals/raw/vendor/chip/scanned_manual.pdf \
  --output manuals/processed \
  --device cuda \
  --ocr-engine rapidocr \
  --force-full-page-ocr
```

For digital chip manuals, prefer `--no-ocr` first.

## Recommended AI Workflow

When an AI assistant is asked to use a processed manual directory, follow this workflow.

### 1. Start with `README.md`

Check:

- page/table/alert counts
- which file to open next
- whether any alerts already indicate distrust zones

### 2. Use `manifest.json`

Check:

- `status`
- `page_count`
- `table_count`
- `alert_count`
- `source_pdf_path`
- `document_markdown`
- `document_html`
- `chunks_index`
- `sections_index`
- `tables_index`

If `alert_count > 0`, inspect `alerts.json` before trusting table-heavy results.

### 3. Use `sections.jsonl` to navigate

Search section names first:

```sh
rg -n "GPIO Matrix|I2C|UART|Register Summary" manuals/processed/<doc_id>/sections.jsonl
```

This gives page ranges and chunk counts.

### 4. Use `chunks.jsonl` for retrieval

Search chunks for detailed passages:

```sh
rg -n "GPIO_FUNC0_IN_SEL_CFG_REG|I2C_SCL_LOW_PERIOD_REG|UART_FIFO_REG" \
  manuals/processed/<doc_id>/chunks.jsonl
```

Prefer `contextualized_text` for answer generation because it includes heading context.

### 5. Use `document.md` for local reading

Open around the relevant heading or page marker. Use it to understand surrounding prose and the document flow.

### 6. Use table sidecars for values

If the answer depends on a table value, follow the table sidecar link:

```text
tables/table_XXXX.csv
```

For high-confidence embedded work, verify:

- the chunk text
- the table sidecar
- the original PDF page when the value is critical

### 7. Use `document.html` or `assets/` for visual content

Use these for:

- timing diagrams
- register bit diagrams
- pin matrices
- wide visual tables
- block diagrams

If an alert points to a figure/table issue, inspect the relevant artifact and original PDF page.

### 7. Cite pages in final engineering answers

Use chunk citations such as:

```text
esp32-s3-technical-reference-manual-en p.501
```

Do not cite a CSV table alone without page context when the answer affects firmware behavior.

## Current Evaluation Results

### ESP32-S3 datasheet

Input:

```text
manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf
```

Output:

```text
manuals/processed/esp32-s3-datasheet-en
```

Observed result:

- `status = success`
- `page_count = 87`
- `table_count = 71`
- `chunks = 309`
- `sections = 141`
- `alert_count = 1`
- alert: `Table 2-9. Peripheral Pin Assignment` falls back to image

Assessment:

- Good for prose, electrical tables, and most datasheet lookup.
- Ultra-wide peripheral pin assignment remains a Docling limitation.

### STM32H743VI datasheet

Input:

```text
manuals/raw/st/stm32h7/stm32h743vi.pdf
```

Output:

```text
manuals/processed/stm32h743vi
```

Observed result:

- `status = success`
- `page_count = 357`
- `table_count = 329`
- `chunks = 1324`
- `sections = 242`
- `alert_count = 0`
- first run emitted a few MathML warnings, but final status was successful

Assessment:

- Strong enough for datasheet-style AI lookup.
- Many table captions were recoverable from context.
- No table-image fallback alert under current detection rules.

### ESP32-S3 Technical Reference Manual

Input:

```text
manuals/raw/espressif/esp32s3/esp32-s3_technical_reference_manual_en.pdf
```

Output:

```text
manuals/processed/esp32-s3-technical-reference-manual-en
```

Observed result:

- `status = success`
- `page_count = 1531`
- `window_count = 7`
- `table_count = 667`
- `chunks = 3775`
- `sections = 1379`
- `alert_count = 9`
- alert type: `empty_table_sidecar`
- `document.json` is large, about 137 MB

Assessment:

- Docling can complete the conversion and produce useful retrieval assets for a 1531-page TRM.
- The 501-750 page window was a major performance hotspot.
- Register and peripheral sections are searchable and chunked.
- Some formula/figure-heavy content degrades, with `formula-not-decoded` markers and empty table sidecars.
- This is good enough for structured lookup, but not perfect enough to treat as a standalone authority without PDF cross-checking.

## Docling Strengths For Embedded Manuals

- Can run locally and reproducibly.
- Good default parser for digital datasheets and TRMs.
- Produces structured JSON, Markdown, and HTML.
- Integrates with native Docling chunking.
- Handles many register summary and electrical tables well enough to be useful.
- Supports image sidecars, table sidecars, and page-aware metadata.
- Works with GPU acceleration through the configured pipeline.
- Avoids locking the project into one downstream consumer.

## Docling Weaknesses Observed

- Ultra-wide matrix tables can fall back to images or be hard to structure.
- Some figures can be misclassified as tables.
- Some table sidecars can be empty.
- Some table captions are missing or need conservative recovery.
- Formula-to-MathML conversion can emit warnings.
- Dense TRM windows can be very slow even with GPU enabled.
- Markdown can contain page furniture and broken words like `T able`.
- Parsed output is useful, but not authoritative.

## Current Recommendation

Use Docling as the default local mainline for embedded manuals.

Do not keep adding heavy heuristics for every parsing defect. The current deterministic improvements are enough for this stage:

- table sidecar export
- table sidecar links in Markdown
- table references in chunks/sections
- caption recovery
- HTML reading copy
- image retention
- quality alerts
- opt-in window cache

For remaining hard cases, especially ultra-wide pin matrices and figure-heavy register diagrams, the next rational step is tool comparison, not deeper Docling-specific patching.

Recommended comparison candidates:

- Marker
- MinerU
- OpenDataLoader PDF

Use `alerts.json`, slow page windows, and known hard pages as the A/B test set.

## Official Docling References

- Main site: https://docling-project.github.io/docling/
- Chunking: https://docling-project.github.io/docling/concepts/chunking/
- Batch conversion: https://docling-project.github.io/docling/examples/batch_convert/
- Table export: https://docling-project.github.io/docling/examples/export_tables/
- Figure export: https://docling-project.github.io/docling/examples/export_figures/
- Visual grounding: https://docling-project.github.io/docling/examples/visual_grounding/
- Full-page OCR: https://docling-project.github.io/docling/examples/full_page_ocr/
