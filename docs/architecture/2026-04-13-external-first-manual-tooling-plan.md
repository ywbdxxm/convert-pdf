# Local-Free Manual Tooling Plan

Date: 2026-04-13

## Position

This project is no longer about building our own PDF/RAG framework.

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

## Candidate Shortlist

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

### 2. Docling Native Integrations

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

### 3. AnythingLLM

Priority: first lightweight UI/document-chat candidate.

Why:

- Local/offline-first desktop app.
- Free/open-source.
- Works with local models, local embedding, local vector DB, and documents.
- Lower operational burden than Dify/RAGFlow.

Risks:

- May not preserve strict PDF page/table evidence well enough.
- Might be a good UI, not a strong parser.

First test:

- Import either the original PDF or parser-generated Markdown from OpenDataLoader/Docling.
- Use local Ollama model and local embedding.
- Check whether answers show useful source citations.

### 4. Dify

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

- Do not start with raw PDF upload.
- First test Dify Knowledge using Markdown output from the best parser candidate.
- Use Ollama/local embeddings to avoid paid APIs.
- Evaluate retrieval testing and citation behavior.

### 5. Kotaemon

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

### 6. Open WebUI + Docling Serve

Priority: optional later UI integration.

Why:

- Useful if the final UX is local chat with Ollama.
- Has a documented Docling document extraction path using Docling Serve.
- Can use local or API picture description modes.

Risks:

- Requires Docling Serve container/service.
- More configuration than a parser smoke test.

### 7. Marker

Priority: parser A/B candidate after OpenDataLoader and Docling native paths.

Why:

- Converts to Markdown, JSON, chunks, and HTML.
- Extracts images.
- Has table-specific and optional LLM-correction paths.

Risks:

- May be slower/heavier.
- Need to verify local GPU requirements and exact output on our manuals.

### 8. MinerU

Priority: parser A/B candidate after OpenDataLoader/Marker if needed.

Why:

- Strong PDF-to-Markdown/JSON project.
- Extracts images, tables, titles, formulas, and more.
- Has CLI/API/WebUI paths.

Risks:

- Heavier dependency footprint.
- We already suspect OpenDataLoader may cover the same need with less GPU dependence.

### 9. PyMuPDF4LLM

Priority: lightweight digital-PDF baseline.

Why:

- Fast and simple.
- Useful to determine whether simpler digital datasheets need heavy parsers at all.

Risk:

- Likely weak for complex tables and diagrams.

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

Goal: decide whether a better parser exists before worrying about RAG UI.

Order:

1. OpenDataLoader PDF local mode
2. Docling native LlamaIndex/LangChain integration
3. PyMuPDF4LLM lightweight baseline
4. Marker if needed
5. MinerU if needed

Test questions:

- Can it locate `Table 2-9. Peripheral Pin Assignment`?
- Does output preserve page numbers?
- Does output preserve table structure?
- Does output expose bounding boxes or visual coordinates?
- Can we map answer evidence back to the original PDF?

### Round 2: Local UI / Knowledge App Tests

Goal: decide whether a ready-made app can replace custom RAG work.

Order:

1. AnythingLLM with parser-generated Markdown
2. Dify with parser-generated Markdown and local Ollama/local embeddings
3. Kotaemon with Docling or best parser output
4. Open WebUI + Docling Serve only if needed

Test questions:

- Can it ingest the best parser output without code?
- Does it show source citations?
- Does retrieval find the correct manual section/table?
- Can it run locally without paid APIs?
- Is setup acceptable on this WSL laptop?

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

## Near-Term Recommendation

Next concrete task:

1. Create a small external-tool trial doc for OpenDataLoader PDF.
2. Install/test OpenDataLoader local mode only if environment impact is acceptable.
3. Run one ESP32-S3 datasheet conversion.
4. Inspect JSON/Markdown/HTML around `Table 2-9`.
5. Decide whether to proceed to hybrid mode or compare Docling integrations.

Do not write project framework code before this.

## References

- OpenDataLoader PDF: https://github.com/opendataloader-project/opendataloader-pdf
- OpenDataLoader site: https://opendataloader.org/
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
