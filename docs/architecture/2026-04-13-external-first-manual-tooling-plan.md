# External-First Manual Tooling Plan

Date: 2026-04-13

## Purpose

This document resets the project direction after the NIH correction.

The goal is no longer to extend the custom `docling_batch` pipeline or build a local evaluation framework. The goal is to find and test mature existing tools, integrations, and best practices for AI-assisted chip manual lookup.

The operating rule is:

> Use existing tools first. Write custom code only after a concrete external-tool gap is proven on real embedded-manual questions.

## Current State

Current assets:

- `docling_batch/` exists and has produced useful artifacts.
- `manuals/processed/<doc_id>/` exists for current Docling baseline outputs.
- `docs/superpowers/specs/2026-04-13-manual-evaluation-framework-design.md` exists, but its proposed custom `manual_eval` framework is no longer the recommended next implementation.
- `.worktrees/manual-eval-framework/` contains uncommitted prototype code and should be treated as abandoned unless explicitly revived.

Current decision:

- Freeze `docling_batch`.
- Do not continue `manual_eval`.
- Do not build custom RAG/index/search layers.
- Research and test mature integrations and products first.

## First-Principles Requirements

The project-specific need is not PDF conversion by itself.

For chip manuals, the useful system must support:

- page-level citation
- source PDF traceability
- table value inspection
- diagram/image inspection
- parser failure or uncertainty visibility
- enough retrieval quality to answer real embedded questions

For register bits, pin mappings, timing limits, and electrical characteristics, the original PDF remains the final authority.

## Priority 1: Docling Ecosystem Integrations

These should be tested before any custom wrapper.

### LlamaIndex + Docling

Why test first:

- Official Docling/LlamaIndex integration exists.
- `DoclingReader` can load Docling JSON format.
- `DoclingNodeParser` can turn Docling documents into LlamaIndex nodes.
- The LlamaIndex example explicitly shows grounding metadata such as page number and bounding boxes.

Test goal:

- Can it answer a datasheet question while preserving page/table/source metadata?

Minimal experiment:

- Use one ESP32-S3 datasheet PDF.
- Use `DoclingReader(export_type=JSON)`.
- Use `DoclingNodeParser`.
- Inspect returned source nodes and metadata before caring about answer quality.

### LangChain + Docling

Why test second:

- Official `langchain-docling` package exists.
- `DoclingLoader` supports `ExportType.DOC_CHUNKS` and `ExportType.MARKDOWN`.
- The LangChain example shows `dl_meta` with headings, page provenance, bounding boxes, and source filename/URL.

Test goal:

- Can `DOC_CHUNKS` preserve enough provenance for embedded-manual citation?

Minimal experiment:

- Load the ESP32-S3 datasheet with `DoclingLoader`.
- Use `ExportType.DOC_CHUNKS`.
- Print first relevant chunks and metadata for `Table 2-9` or a GPIO/pin mux query.

### Haystack + Docling

Why test third:

- `docling-haystack` exists and provides `DoclingConverter`.
- It supports Docling converter configuration, conversion kwargs, export type, chunker, and metadata extractor.

Test goal:

- Decide whether Haystack's pipeline style adds value over LlamaIndex/LangChain for this project.

## Priority 2: Existing RAG / Document QA Applications

These are likely better than building our own UI or retrieval framework.

### Kotaemon

Why test:

- Open-source document QA/RAG UI.
- Supports Docling as a local open-source document parser.
- Provides hybrid RAG, citations, in-browser PDF preview, figure/table support, and configurable retrieval settings.

Test goal:

- Can a non-custom UI answer chip manual questions with useful citations and PDF preview?

### RAGFlow

Why test:

- Full RAG platform with UI/API.
- Parser component offers PDF parser options including DeepDoc, Naive, MinerU, Docling, and third-party vision models.
- Provides chunk visualization, citations, multi-recall, reranking, and parser pipelines.

Test goal:

- Can RAGFlow replace our custom manual-processing and RAG ambitions?

Important caveat:

- MinerU in RAGFlow requires an accessible MinerU API service.

### Open WebUI + Docling Serve

Why test later:

- Open WebUI can use Docling Serve as document extraction backend.
- Docling Serve has CPU/CUDA containers and a stable API service.

Why not first:

- It adds container/service complexity.
- Large document performance may need careful configuration.
- It is more of a UI integration trial than a parser-quality trial.

### Dify / AnythingLLM

Why lower priority:

- Good generic document app platforms.
- Less obviously suited for strict page/table/image provenance in technical chip manuals.
- Useful after parser and citation quality are understood.

## Priority 3: Converter / Parser Alternatives

These test whether Docling itself is the right parser.

### Marker

Why test:

- Converts documents to Markdown, JSON, chunks, and HTML.
- Extracts images.
- Handles tables, forms, equations, links, and code blocks.
- Has table-specific conversion and optional LLM correction.

Test goal:

- Compare Marker against Docling on wide tables, table JSON, and visual/manual readability.

### MinerU

Why test:

- Converts PDF/image/DOCX to Markdown and JSON.
- Removes headers/footers/footnotes/page numbers.
- Preserves headings/paragraphs/lists.
- Extracts images, image descriptions, tables, table titles, and footnotes.
- Converts formulas to LaTeX.
- Offers CLI/API/WebUI routes.

Test goal:

- Compare MinerU against Docling/Marker on formulas, long manuals, and table-heavy pages.

### Unstructured

Why test:

- Provides typed elements and metadata.
- Supports page metadata, hierarchy metadata, image/table extraction options, and table `text_as_html`.

Test goal:

- See if its element model is better for source-grounded RAG ingestion than our custom JSONL.

### PyMuPDF4LLM

Why test:

- Lightweight and fast.
- Converts PDF pages to Markdown.
- Supports page chunks.

Test goal:

- Use as a low-cost baseline for digital datasheets.

## Smoke Test Questions

Use the same questions across candidates:

- ESP32-S3 datasheet: locate `Table 2-9. Peripheral Pin Assignment`.
- ESP32-S3 datasheet: answer one GPIO/pin mux question with page citation.
- ESP32-S3 datasheet: answer one electrical characteristic value with page citation.
- STM32H743VI datasheet: inspect a table-heavy section.
- ESP32-S3 TRM: locate an I2C register summary.
- ESP32-S3 TRM: inspect one formula/figure-heavy section.

## Evaluation Checklist

For each candidate, answer:

- Can it run without custom code beyond documented setup?
- Does it preserve page numbers?
- Does it expose source chunks/nodes/documents?
- Does it preserve bounding boxes or equivalent provenance?
- Can tables be inspected in raw or rendered form?
- Can images/diagrams be inspected or cited?
- Does it expose parser uncertainty, debug output, or chunk visualization?
- How much setup is required?
- How much disk/GPU/CPU does it need?
- Can it work locally?
- Does it reduce custom code?

## Proposed Trial Order

### Round 1: Docling Integrations

1. LlamaIndex + Docling
2. LangChain + Docling
3. Haystack + Docling

Stop if one clearly satisfies metadata and workflow needs.

### Round 2: UI / App Trials

1. Kotaemon + Docling
2. RAGFlow with Docling parser
3. RAGFlow with MinerU parser, only if MinerU service setup is acceptable
4. Open WebUI + Docling Serve

### Round 3: Parser Alternatives

1. Marker
2. MinerU standalone
3. Unstructured
4. PyMuPDF4LLM

## What Not To Do

- Do not implement `manual_eval`.
- Do not continue `docling_batch` feature development.
- Do not build custom chunking/search/RAG code.
- Do not normalize every tool's output into our old schema.
- Do not assume `manuals/processed/<doc_id>` is the final shape.

## References

- Docling LlamaIndex integration: https://docling-project.github.io/docling/integrations/llamaindex/
- LlamaIndex DoclingReader demo: https://docs.llamaindex.ai/en/stable/examples/data_connectors/DoclingReaderDemo/
- LangChain DoclingLoader: https://docs.langchain.com/oss/python/integrations/document_loaders/docling
- Haystack Docling integration: https://docling-project.github.io/docling/integrations/haystack/
- Docling Haystack GitHub: https://github.com/docling-project/docling-haystack
- Kotaemon: https://github.com/Cinnamon/kotaemon
- Kotaemon loaders: https://cinnamon.github.io/kotaemon/reference/loaders/
- RAGFlow parser component: https://ragflow.com.cn/docs/parser_component
- Open WebUI Docling extraction: https://docs.openwebui.com/features/rag/document-extraction/docling/
- Docling Serve: https://github.com/docling-project/docling-serve
- Marker: https://github.com/datalab-to/marker
- MinerU: https://github.com/opendatalab/MinerU
- Unstructured partition elements: https://docs.unstructured.io/api-reference/legacy-api/partition/document-elements
- Unstructured partition parameters: https://docs.unstructured.io/api-reference/legacy-api/partition/api-parameters
- PyMuPDF4LLM: https://github.com/pymupdf/pymupdf4llm
