# Findings

## Current Direction

The project direction is now external-first and agentic-file-retrieval-first:

- Do not build custom PDF/RAG frameworks.
- Do not continue `manual_eval`.
- Do not add new features to `docling_batch`.
- Prefer local/free/self-hosted tools.
- Avoid paid remote parser/OCR APIs by default.
- Prefer "PDF -> structured files -> Codex/agent reads the folder" over traditional RAG systems.
- Use real embedded-manual questions to decide tools.

## Environment Constraints

- Target machine: WSL2 laptop with RTX 4060 Laptop GPU.
- Prefer tools that can run locally on CPU/GPU.
- Docker is acceptable, but heavy multi-service stacks should be justified.
- Avoid paid remote APIs unless explicitly approved later.

## Tool Shortlist

### Highest Priority

- `OpenDataLoader PDF`
  - Local parser with Markdown/JSON/HTML outputs.
  - Claims JSON with page numbers and bounding boxes.
  - Claims no GPU required in local mode.
  - Has LangChain integration.
  - Must be verified on our real chip manuals; benchmark claims are project-provided.

- `OpenDataLoader PDF + LangChain`
  - Official `langchain-opendataloader-pdf` loader exists.
  - LangChain docs describe it as local, deterministic, fast, Markdown/JSON output with bounding boxes.
  - Should be tested as OpenDataLoader's paired consumer, but only after raw file output is inspected.

- `Docling + LlamaIndex`
  - Official Docling integration.
  - `DoclingReader` can load Docling JSON.
  - `DoclingNodeParser` converts Docling documents into LlamaIndex nodes.

- `Docling + LangChain`
  - `DoclingLoader` supports `DOC_CHUNKS` and `MARKDOWN`.
  - Useful to inspect chunk metadata without our wrapper.

### Good Local UI Candidates

- `Dify`
  - Self-hosted Docker Compose platform.
  - Useful as a knowledge app only after parser output is chosen.
  - Not the core path; agentic folder reading has priority.

- `AnythingLLM`
  - Local/offline-friendly document chat.
  - Lightweight app fallback if folder-based agent workflow is not enough.

- `Kotaemon`
  - Local document QA UI with hybrid RAG, citations, PDF preview, local model support, and Docling parser option.

### Secondary Parser Candidates

- `PyMuPDF4LLM`
  - Fast lightweight digital-PDF baseline.

- `Marker`
  - Strong parser candidate for Markdown/JSON/HTML/images/tables; potentially heavier.

- `MinerU`
  - Strong parser candidate for tables/formulas/images; potentially heavier.

## Deferred / Excluded

- `RAGFlow`
  - Too heavy for current needs.
  - Reconsider only if lighter apps fail.

- `Unstructured`
  - Deferred because user does not want paid/remote routes.

- Paid parser/OCR APIs
  - Excluded by default: LlamaParse cloud, Mistral OCR API, Azure Document Intelligence, Mathpix, commercial Unstructured paths.

## Frozen Baseline

`docling_batch` remains useful as a baseline:

- It has existing outputs for ESP32-S3 datasheet, ESP32-S3 TRM, and STM32H743VI.
- It should not be extended.
- It can be used only for comparison against external tools.

## Fixed Evaluation Questions

- Locate `Table 2-9. Peripheral Pin Assignment` in ESP32-S3 datasheet.
- Find one GPIO/pin mux fact and cite the page.
- Find one electrical characteristic table value and cite the page.
- Inspect a table-heavy STM32H743VI section.
- Locate I2C or UART register summary in ESP32-S3 TRM.
- Inspect a formula/figure-heavy section.

## Decision Rule

Choose the tool that answers real manual questions with the least custom code while preserving:

- page citation
- source PDF traceability
- table inspectability
- diagram/image inspectability
- parser uncertainty visibility

The original PDF remains final authority for engineering conclusions.

## Agentic File Retrieval Candidates

Priority combinations for the main workflow:

1. `OpenDataLoader PDF local mode -> folder of Markdown/JSON/HTML -> Codex reads/searches files directly`
2. `OpenDataLoader PDF local mode -> LangChain OpenDataLoaderPDFLoader -> inspect documents/metadata, not necessarily build RAG`
3. `Docling native/LlamaIndex -> inspect nodes/metadata as files or printed artifacts`
4. `Docling native/LangChain DOC_CHUNKS -> inspect chunks/metadata`
5. `PyMuPDF4LLM -> Markdown/page chunks -> Codex direct file search`
6. `Marker or MinerU -> exported files -> Codex direct file search`, only if earlier parsers fail

Traditional RAG/UI tools are secondary consumers:

1. `OpenDataLoader/Docling Markdown -> Dify Knowledge`
2. `OpenDataLoader/Docling Markdown -> AnythingLLM`
3. `Kotaemon/Open WebUI`, only if a UI becomes important

## Key References

- OpenDataLoader PDF: https://github.com/opendataloader-project/opendataloader-pdf
- OpenDataLoader PDF LangChain integration: https://docs.langchain.com/oss/python/integrations/document_loaders/opendataloader_pdf
- OpenDataLoader RAG integration guide: https://opendataloader.org/docs/rag-integration
- Dify Knowledge: https://docs.dify.ai/en/use-dify/knowledge/readme
- Dify self-host Docker Compose: https://docs.dify.ai/en/self-host/quick-start/docker-compose
- AnythingLLM: https://anythingllm.com/
- Kotaemon: https://github.com/Cinnamon/kotaemon
- Open WebUI Docling extraction: https://docs.openwebui.com/features/rag/document-extraction/docling/
- Docling LlamaIndex integration: https://docling-project.github.io/docling/integrations/llamaindex/
- LangChain Docling loader: https://docs.langchain.com/oss/python/integrations/document_loaders/docling
- Marker: https://github.com/datalab-to/marker
- MinerU: https://github.com/opendatalab/MinerU
- PyMuPDF4LLM: https://github.com/pymupdf/pymupdf4llm
