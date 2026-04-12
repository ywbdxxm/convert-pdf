# Findings

## Current Direction

The mainline is intentionally narrow:

1. `docling_batch` existing output as frozen baseline
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

`docling_batch` is useful only as a baseline:

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

- a good `docling_batch`-specific bundle
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
