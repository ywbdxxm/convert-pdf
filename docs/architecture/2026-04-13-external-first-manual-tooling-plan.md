# Local-Free Manual Tooling Plan

Date: 2026-04-13

## Position

This project is no longer about building our own PDF/RAG framework.

The primary workflow is agentic file retrieval:

```text
PDF -> existing parser/converter -> structured files -> Codex/agent searches and reads the folder -> original PDF verification
```

Traditional RAG tools are optional consumers, not the core architecture.

The priority is:

1. Use mature existing tools first.
2. Keep all processing local or self-hosted when practical.
3. Avoid paid remote APIs by default.
4. Avoid heavyweight platforms unless lighter tools fail.
5. Write custom code only after a concrete gap is proven on real chip manuals.

Current machine context:

- WSL2 on a laptop with RTX 4060 Laptop GPU
- Docker and NVIDIA runtime are available
- A shared AI base exists at `/home/qcgg/.mamba/envs/ai-base-cu124-stable`
- `docling_batch` exists, but is now a frozen baseline, not a growth target

## What We Are Not Doing

- Do not add features to `docling_batch`.
- Do not revive `manual_eval`.
- Do not build custom RAG/search/index layers.
- Do not start with RAGFlow. It is too heavy for the current exploration need.
- Do not test paid/remote-first parsing such as paid Unstructured paths.
- Do not assume `manuals/processed/<doc_id>` is the universal output shape.
- Do not make traditional RAG the default workflow when an agent can read structured files directly.

## Evaluation Principle

For embedded manuals, the winning tool must help answer questions while preserving evidence:

- page number
- source PDF path
- table value inspectability
- diagram/image inspectability
- source chunk visibility
- parser failure or uncertainty visibility
- low setup and maintenance burden

The original PDF remains final authority for register bits, pin mappings, timing limits, and electrical characteristics.

## Architecture Preference

Preferred:

```text
OpenDataLoader/Docling/other parser output
  -> Markdown / JSON / HTML / images / tables
  -> Codex reads files directly with grep/open/table inspection
  -> original PDF page check for critical facts
```

Secondary:

```text
Parser output
  -> LangChain/LlamaIndex loader
  -> inspect documents/nodes/chunks and metadata
  -> optionally feed a UI or RAG app
```

Not preferred as default:

```text
Raw PDF
  -> black-box RAG app
  -> answer without transparent file artifacts
```

## Candidate Shortlist

### 0. `docling_batch` Existing Output

Priority: frozen baseline.

Why:

- It already produced useful local file assets: Markdown, JSON, HTML, chunks, sections, tables, alerts.
- It represents the current custom approach.
- It lets us measure whether external tools actually improve quality or reduce code.

Rules:

- Do not add features.
- Do not fix heuristics unless a later decision explicitly keeps this path.
- Compare against it using existing outputs only.

If later unfrozen, acceptable improvements are narrow:

- add page-level slices such as `pages/page_0027.md` or `pages/page_0027.json`
- add a generated folder entrypoint such as `README.generated.md` or `index.json`
- add a concise `quality-summary.md` from existing table/alert/chunk metadata
- add optional hard-page images for pages flagged by alerts
- add Docling-native chunk export beside custom filtered chunks for comparison

Do not use `docling_batch` as a place to build:

- RAG/search/vector DB
- more fragile table parser heuristics
- VLM repair workflows
- multi-tool orchestration
- UI/application logic

First test:

- Use existing ESP32-S3 datasheet output.
- Ask Codex to locate `Table 2-9` from the folder.
- Record where it succeeds and where it requires PDF fallback.

### 1. OpenDataLoader PDF

Priority: highest parser candidate.

Why:

- Local-first parser.
- Outputs Markdown, JSON with bounding boxes, and HTML.
- Requires Java 11+ and Python 3.10+.
- Claims element-level page numbers and bounding boxes, useful for citations.
- Claims local mode needs no GPU.
- Has LangChain integration.
- Hybrid mode also runs locally, but should be treated as a second step because it adds a backend service.

Risks:

- Its benchmark claims are from the project itself; we must verify on our chip manuals.
- Hybrid mode may add complexity even if it is local.
- It may be excellent for document layout but still need RAG/UI integration.

First test:

- Run local non-hybrid mode on ESP32-S3 datasheet.
- Inspect JSON for `Table 2-9`, page number, bounding boxes, and table structure.
- Compare against current Docling baseline and original PDF page.

### 2. OpenDataLoader PDF + LangChain

Priority: highest consumer/library candidate for OpenDataLoader output.

Why:

- OpenDataLoader has an official LangChain package: `langchain-opendataloader-pdf`.
- LangChain's OpenDataLoader PDF docs describe local, deterministic, fast PDF parsing with Markdown/JSON output and bounding boxes.
- OpenDataLoader's own RAG guide documents integration-oriented usage instead of only standalone conversion.
- This is the direct paired consumer path and should be tested before generic app UIs.
- For this project, the first goal is metadata inspection, not building a vector index.

Risks:

- LangChain adds framework overhead.
- The loader may expose documents/chunks in a way that is convenient for RAG but less transparent than raw JSON.
- We must inspect metadata directly before judging answer quality.

First test:

- Use `OpenDataLoaderPDFLoader` on the ESP32-S3 datasheet.
- Inspect returned LangChain documents and metadata for `Table 2-9`.
- Verify whether page number, bbox, and source path survive loader conversion.
 - Save or print representative documents/chunks so Codex can inspect them as files.

### 3. OpenDataLoader PDF + Dify

Priority: app/workflow candidate after agentic folder workflow is verified.

Why:

- Dify is self-hostable and can use local model providers such as Ollama.
- Dify Knowledge can ingest parser-produced Markdown rather than relying on Dify's own PDF extraction.
- If OpenDataLoader produces strong Markdown, Dify can be tested as the knowledge-base/UI layer.

First test:

- Feed OpenDataLoader Markdown into Dify Knowledge.
- Use local Ollama/local embeddings.
- Evaluate retrieval testing and source display behavior.

### 4. Docling Native Integrations

Priority: high, but not via custom `docling_batch`.

Test these mature integration paths:

- LlamaIndex `DoclingReader` + `DoclingNodeParser`
- LangChain `DoclingLoader` with `ExportType.DOC_CHUNKS`
- Haystack `DoclingConverter`, only if LlamaIndex/LangChain are not enough

Why:

- They use Docling without us hand-building a full wrapper.
- They are designed for RAG ingestion.
- They expose document/chunk metadata that may already solve our page/source needs.

First test:

- Use ESP32-S3 datasheet.
- Query or inspect chunks around `Table 2-9`.
- Verify metadata: page, source, heading, table or bounding-box provenance.

### 5. LiteParse

Priority: high agentic-file-retrieval candidate.

Why:

- Local-first parser from the LlamaIndex ecosystem.
- Designed for coding agents and local workflows.
- Parses PDFs with spatial layout and bounding boxes.
- Can generate page screenshots for LLM/agent workflows.
- No cloud dependencies, LLMs, or API keys.

Risks:

- May produce lower-level spatial text rather than polished Markdown.
- Table reconstruction may require the agent to reason from layout/screenshots.
- Node.js/npm dependency may be new for this workstation.

First test:

- Parse ESP32-S3 datasheet with LiteParse.
- Generate a screenshot for page 27.
- Check whether text/bbox output plus screenshot lets Codex locate `Table 2-9`.

### 6. AnythingLLM

Priority: lightweight UI/document-chat fallback.

Why:

- Local/offline-first desktop app.
- Free/open-source.
- Works with local models, local embedding, local vector DB, and documents.
- Lower operational burden than Dify/RAGFlow.

Risks:

- May not preserve strict PDF page/table evidence well enough.
- Might be a good UI, not a strong parser or evidence workflow.

First test:

- Import either the original PDF or parser-generated Markdown from OpenDataLoader/Docling.
- Use local Ollama model and local embedding.
- Check whether answers show useful source citations.

### 7. Dify

Priority: workflow/app platform candidate, not first parser candidate.

Why:

- Self-hostable with Docker Compose.
- Has Knowledge/RAG concepts, retrieval testing, metadata, retrieval strategy configuration.
- Supports local models via Ollama and local embedding models.
- Good if we want to build a repeatable app/workflow around manual lookup.

Risks:

- Docker deployment starts many services and is heavier than AnythingLLM.
- Built-in PDF parsing may not be the best for chip manuals.
- Best used after we decide the parser/Markdown source, not before.

First test:

- Prefer OpenDataLoader or Docling-generated Markdown.
- Use Ollama/local embeddings to avoid paid APIs.
- Evaluate retrieval testing and citation behavior.

### 8. Kotaemon

Priority: optional UI/RAG candidate after AnythingLLM.

Why:

- Open-source document QA UI.
- Supports local models through Ollama.
- Has hybrid RAG, citations, in-browser PDF preview, and multimodal parsing options.
- Supports Docling as a local parser option.

Risks:

- More moving parts than a simple parser test.
- Some advanced document parsing options involve extra dependencies.

First test:

- Use Docker lite or local install.
- Test Docling loader on ESP32-S3 datasheet.
- Check citation/PDF-preview quality.

### 9. Open WebUI + Docling Serve

Priority: optional later UI integration.

Why:

- Useful if the final UX is local chat with Ollama.
- Has a documented Docling document extraction path using Docling Serve.
- Can use local or API picture description modes.

Risks:

- Requires Docling Serve container/service.
- More configuration than a parser smoke test.

### 10. PyMuPDF4LLM

Priority: lightweight digital-PDF baseline.

Why:

- Fast and simple.
- Useful to determine whether simpler digital datasheets need heavy parsers at all.

Risk:

- Likely weak for complex tables and diagrams.

### 11. MarkItDown

Priority: lightweight Markdown baseline.

Why:

- Microsoft-maintained local converter.
- Converts PDFs and many other document types to Markdown.
- Very easy to run and useful as a cheap baseline.

Risks:

- Intended for text analysis pipelines, not high-fidelity technical document conversion.
- Likely weak for table/page/bbox evidence.

### 12. PaperFlow

Priority: parser-output post-processing candidate.

Why:

- Local Web UI and API.
- Parser-agnostic post-processing layer.
- Can use PyMuPDF for fast digital PDFs or PaddleOCR-VL for scans/formulas/complex layouts.
- Produces structured Markdown with footnotes, figure links, and metadata.

Risks:

- It is a post-processing layer, not necessarily a primary parser.
- May introduce another layer of abstraction before parser quality is understood.

### 13. PaddleOCR-VL / PP-StructureV3

Priority: hard-page OCR/layout candidate.

Why:

- Local document parsing/OCR path for text, layout, tables, formulas, and Markdown output.
- PaddleOCR documentation includes MCP server integration for large-model applications.
- More relevant for scanned/image-heavy or formula-heavy pages.

Risks:

- Heavier model/dependency setup.
- Digital datasheets may not need it.

### 14. Marker

Priority: parser A/B candidate after OpenDataLoader and Docling native paths.

Why:

- Converts to Markdown, JSON, chunks, and HTML.
- Extracts images.
- Has table-specific and optional LLM-correction paths.

Risks:

- May be slower/heavier.
- Need to verify local GPU requirements and exact output on our manuals.

### 15. MinerU

Priority: parser A/B candidate after OpenDataLoader/Marker if needed.

Why:

- Strong PDF-to-Markdown/JSON project.
- Extracts images, tables, titles, formulas, and more.
- Has CLI/API/WebUI paths.

Risks:

- Heavier dependency footprint.
- We already suspect OpenDataLoader may cover the same need with less GPU dependence.

### 16. HURIDOCS PDF Document Layout Analysis

Priority: local service candidate.

Why:

- Docker-powered PDF layout analysis service with Gradio UI and REST API.
- Supports OCR, segmentation/classification, reading order, Markdown/HTML conversion, and visual overlays.
- Can be useful if page visualization becomes important.

Risks:

- Heavier service-style setup than CLI parsers.
- Not first-round unless CLI/local parser outputs are insufficient.

### 17. Markdrop / pdfmd

Priority: fallback community tools.

Why:

- Focused on PDF-to-Markdown, images, tables, GUI/preview workflows.
- Markdrop specifically targets table/image preservation.

Risks:

- Lower confidence and maturity than the main candidates.
- Keep as fallback only.

## Excluded Or Deferred

### RAGFlow

Deferred.

Reason:

- Too heavy for current exploration.
- Useful only if lighter local tools fail and we need a full RAG platform.

### Unstructured

Excluded for now.

Reason:

- User does not want paid/remote API routes.
- Local/open-source pieces exist, but the project is not the best fit for current free/local-first exploration.

### Paid OCR / parser APIs

Excluded by default.

Examples:

- LlamaParse cloud
- Mistral OCR API
- Azure Document Intelligence
- Mathpix
- commercial Unstructured paths

## Trial Plan

### Round 0: Freeze Current Baseline

Do not modify `docling_batch`.

Use existing processed outputs only as a reference baseline:

- ESP32-S3 datasheet
- STM32H743VI datasheet
- ESP32-S3 TRM

### Round 1: Parser Smoke Tests

Goal: decide whether a better parser/file artifact generator exists before worrying about RAG UI.

Order:

0. Current `docling_batch` output as frozen baseline
1. OpenDataLoader PDF local mode
2. OpenDataLoader PDF + LangChain loader for metadata inspection
3. LiteParse local parser + screenshot workflow
4. Docling native LlamaIndex/LangChain integration
5. PyMuPDF4LLM lightweight baseline
6. MarkItDown lightweight Markdown baseline
7. PaperFlow with PyMuPDF upstream, if Markdown post-processing looks useful
8. Marker if needed
9. MinerU if needed
10. PaddleOCR-VL / HURIDOCS only for hard pages or scanned/image-heavy cases

Test questions:

- Can it locate `Table 2-9. Peripheral Pin Assignment`?
- Does output preserve page numbers?
- Does output preserve table structure?
- Does output expose bounding boxes or visual coordinates?
- Can we map answer evidence back to the original PDF?

### Round 2: Local UI / Knowledge App Tests

Goal: decide whether a ready-made app adds value after the agentic file workflow is proven.

Order:

1. Dify with OpenDataLoader-generated Markdown and local Ollama/local embeddings
2. AnythingLLM with parser-generated Markdown
3. Kotaemon with Docling or best parser output
4. Open WebUI + Docling Serve only if needed

Test questions:

- Can it ingest the best parser output without code?
- Does it show source citations?
- Does retrieval find the correct manual section/table?
- Can it run locally without paid APIs?
- Is setup acceptable on this WSL laptop?
- Does it preserve more evidence than direct folder inspection, or only add UI convenience?

### Round 3: Expanded Manual Test

Only after Round 1/2 produce a promising candidate.

Use:

- ESP32-S3 TRM
- STM32H743VI datasheet

Test:

- register summary lookup
- electrical table lookup
- formula/figure-heavy page
- long-document ingestion time
- disk and memory cost

## Decision Matrix

Use simple 0-3 scoring:

- `0`: fails
- `1`: works only with manual workaround
- `2`: usable with caveats
- `3`: strong

Score dimensions:

- local/free fit
- setup cost
- parser quality
- table quality
- page/source citation
- visual traceability
- RAG/UI usefulness
- maintenance burden

The winner is not the tool with the most features. The winner is the tool that answers real chip manual questions with the least custom code.

For this project, a file-output parser can beat a RAG app if Codex can inspect its folder reliably.

## Near-Term Recommendation

Next concrete task:

1. Create a small external-tool trial doc for OpenDataLoader PDF.
2. Install/test OpenDataLoader local mode only if environment impact is acceptable.
3. Run one ESP32-S3 datasheet conversion.
4. Inspect JSON/Markdown/HTML around `Table 2-9`.
5. Test the official OpenDataLoader LangChain loader on the same PDF/output.
6. Decide whether direct Codex folder inspection is already enough.
7. Only then decide whether Dify should consume OpenDataLoader Markdown next.

Parallel low-cost check:

- Run or inspect LiteParse setup because it is explicitly designed for agentic workflows.
- Keep `docling_batch` output open as the baseline comparison folder.

Do not write project framework code before this.

## References

- OpenDataLoader PDF: https://github.com/opendataloader-project/opendataloader-pdf
- OpenDataLoader site: https://opendataloader.org/
- OpenDataLoader PDF LangChain integration: https://docs.langchain.com/oss/python/integrations/document_loaders/opendataloader_pdf
- OpenDataLoader RAG integration guide: https://opendataloader.org/docs/rag-integration
- LiteParse docs: https://developers.llamaindex.ai/liteparse/
- Microsoft MarkItDown: https://github.com/microsoft/markitdown
- PaperFlow: https://www.paperflowing.com/
- PaddleOCR MCP server: https://www.paddleocr.ai/main/en/version3.x/deployment/mcp_server.html
- HURIDOCS PDF Document Layout Analysis: https://github.com/huridocs/pdf-document-layout-analysis
- Markdrop: https://github.com/shoryasethia/markdrop
- Dify Knowledge: https://docs.dify.ai/en/use-dify/knowledge/readme
- Dify self-host Docker Compose: https://docs.dify.ai/en/self-host/quick-start/docker-compose
- Dify model providers: https://docs.dify.ai/en/use-dify/workspace/model-providers
- AnythingLLM: https://anythingllm.com/
- AnythingLLM docs: https://docs.anythingllm.com/
- Kotaemon: https://github.com/Cinnamon/kotaemon
- Open WebUI Docling extraction: https://docs.openwebui.com/features/rag/document-extraction/docling/
- Docling LlamaIndex integration: https://docling-project.github.io/docling/integrations/llamaindex/
- LangChain Docling loader: https://docs.langchain.com/oss/python/integrations/document_loaders/docling
- Marker: https://github.com/datalab-to/marker
- MinerU: https://github.com/opendatalab/MinerU
- PyMuPDF4LLM: https://github.com/pymupdf/pymupdf4llm
