# Docling / OpenDataLoader Mainline Plan

Date: 2026-04-13

## Position

The mainline is intentionally narrow.

This project is now trying to answer one focused question:

> For agentic file retrieval on local chip manuals, is `Docling` or `OpenDataLoader PDF` the better path?

Primary architecture:

```text
PDF -> parser -> structured files -> Codex reads/searches the folder -> original PDF verification
```

Not primary architecture:

```text
PDF -> generic RAG app -> opaque answer
```

## Mainline Comparison Set

### 0. `docling_bundle` Existing Output

Role:

- frozen baseline
- historical reference output
- no new features

### 1. `Docling` Native Output

Role:

- clean baseline for Docling itself
- separates Docling core capability from `docling_bundle` custom packaging

Outputs to inspect:

- JSON
- Markdown
- HTML
- images / artifacts if available

### 2. `OpenDataLoader PDF` Local Mode

Role:

- first direct challenger to Docling

Focus:

- page number
- bounding box metadata
- table quality
- HTML readability

### 3. `OpenDataLoader PDF` Hybrid Mode

Role:

- local follow-up only if local mode table quality is insufficient

Constraint:

- use local `docling-fast` backend

### 4. `OpenDataLoader PDF + LangChain`

Role:

- metadata spot-check only
- not a runtime architecture choice

Question:

- does the official OpenDataLoader LangChain loader preserve page / bbox / source metadata?

### 5. `Docling + LlamaIndex / LangChain`

Role:

- metadata spot-check only
- not a runtime architecture choice

Question:

- do the official Docling consumers preserve page / source / chunk metadata cleanly enough?

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
- HURIDOCS PDF Document Layout Analysis
- Markdrop / pdfmd
- RAGFlow
- Unstructured
- paid or remote parser/OCR APIs

## Comparison Questions

Judge the mainline only on:

- page citation
- source PDF traceability
- bounding boxes or equivalent spatial metadata
- table visibility and inspectability
- raw file readability by Codex
- ability to return to the original PDF page

The original PDF remains final authority for register bits, pin mappings, timing limits, and electrical characteristics.

## Immediate Test Order

1. Use existing `docling_bundle` output as baseline.
2. Generate `Docling` native output for the ESP32-S3 datasheet.
3. Run `OpenDataLoader PDF` local mode on the same PDF.
4. If local mode table quality is weak, run `OpenDataLoader PDF` hybrid mode with local `docling-fast`.
5. Run `OpenDataLoader PDF + LangChain` only to inspect metadata retention.
6. Run `Docling + LlamaIndex` / `Docling + LangChain` only to inspect metadata retention.
7. Decide whether direct Codex folder inspection is already enough.

## References

- OpenDataLoader PDF: https://github.com/opendataloader-project/opendataloader-pdf
- OpenDataLoader PDF LangChain integration: https://docs.langchain.com/oss/python/integrations/document_loaders/opendataloader_pdf
- OpenDataLoader RAG integration guide: https://opendataloader.org/docs/rag-integration
- OpenDataLoader Hybrid Mode: https://opendataloader.org/docs/hybrid-mode
- Docling LlamaIndex integration: https://docling-project.github.io/docling/integrations/llamaindex/
- LangChain Docling loader: https://docs.langchain.com/oss/python/integrations/document_loaders/docling
