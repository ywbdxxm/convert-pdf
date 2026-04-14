# RAG For Embedded Manual Lookup

Date: 2026-04-12

## Purpose

This document explains what RAG means for this repository and how it relates to the current Docling-based manual-processing pipeline.

The practical question is:

> We want chip manuals converted into something an AI assistant can understand, search, cite, and verify. What is the best practice, and do we need RAG software now?

Short answer:

- RAG is a runtime retrieval-and-answering pattern, not a PDF conversion method.
- The current Docling pipeline already creates a RAG-ready corpus.
- For the current scale, RAG is an optional convenience layer, not a fundamental requirement.
- Existing open-source RAG applications should be tried before building more custom infrastructure.
- Only build a small local adapter if existing tools cannot preserve our embedded-manual evidence contract.

## What RAG Is

RAG means Retrieval-Augmented Generation.

In plain terms:

```text
user question
  -> retrieve relevant external evidence
  -> give evidence to the model
  -> generate an answer with citations
```

The important point is that the model is not expected to memorize every chip manual. Instead, the model should read the relevant manual fragments at answer time.

For embedded manuals, the retrieved evidence should include:

- nearby prose from the manual
- chapter/section context
- page numbers
- table sidecars
- image/page artifacts when the answer depends on visual content
- alerts when the parsed content is known to be risky
- links back to the original PDF

## Why Docling Talks About RAG

Docling often mentions RAG because its output is suitable for the ingestion side of a RAG system.

Docling can produce:

- a structured `DoclingDocument`
- Markdown and HTML reading copies
- document-aware chunks
- metadata such as headings and provenance
- table and image artifacts

Docling's official chunking direction is especially relevant: chunking can operate on the structured document, not only on exported Markdown text. `HybridChunker` combines document hierarchy with tokenizer-aware chunk sizing, and `contextualize(chunk)` produces metadata-enriched text for downstream embeddings or generation.

That is why the current repository uses `HybridChunker` and writes `contextualized_text` into `chunks.jsonl`.

## Current Repository State

The current pipeline is:

```text
raw PDF
  -> Docling DocumentConverter
  -> document.json
  -> document.md / document.html
  -> chunks.jsonl / sections.jsonl
  -> tables/*.csv / tables/*.html
  -> artifacts/
  -> alerts.json
```

This is already the corpus-preparation part of RAG.

Current strengths:

- `document.json` is the canonical structured parse.
- `document.md` and `document.html` are readable companions.
- `chunks.jsonl` contains page-aware retrieval units.
- `sections.jsonl` supports navigation by topic/chapter.
- `tables/*.csv` and `tables/*.html` preserve table values for verification.
- `alerts.json` exposes parser-risk pages instead of hiding them.
- `manifest.json` ties everything back to the original PDF and conversion settings.

Current missing pieces for a complete RAG application:

- embedding generation
- persistent lexical/vector/hybrid index
- query handling
- metadata filters
- optional re-ranking
- context packing
- answer policy enforcement
- user-facing query interface

Therefore the current state is:

```text
RAG-ready corpus preparation, not yet a full RAG runtime.
```

## Scope Reality Check

The previous design notes listed the components of a complete RAG runtime:

- embeddings
- lexical/vector/hybrid index
- retriever
- re-ranker
- context packer
- answer policy
- UI or API

That list is accurate as a decomposition of a production RAG stack, but it does not mean this repository should implement all of it now.

For the current use case, the decision rule should be:

```text
If an AI assistant can answer well by reading manifest/chunks/sections/tables/alerts directly,
do not build a RAG runtime.

If lookup becomes repetitive or spans many manuals,
try an existing RAG application first.

If existing tools lose page/table/alert/PDF verification metadata,
then build only the smallest adapter needed to preserve that metadata.
```

This repository should not become a general RAG platform.

The core value we have already built is embedded-manual-aware corpus preparation:

- page-aware chunks
- section navigation
- table sidecars
- alerts for parser risk
- explicit original-PDF authority

That is the part generic RAG tools usually do not understand well enough for firmware work.

## First-Principles Design

The first principle is not "use a vector database."

The first principle is:

> At answer time, the AI assistant should see the smallest sufficient set of reliable manual evidence, with page-level provenance and a way to verify critical values.

For chip manuals, this matters because wrong answers can create real firmware or hardware mistakes:

- wrong register bit
- wrong reset value
- wrong pin mux
- wrong timing limit
- wrong voltage/current limit
- wrong errata condition

That means the durable artifact stack should remain:

```text
raw PDF as authority
Docling JSON as canonical machine representation
Markdown/HTML for reading
chunks/sections for retrieval
CSV/HTML sidecars for table values
artifacts/page images for visual facts
alerts for parser risk
```

RAG should sit on top of this stack. It should not replace it.

## What RAG Would Improve

RAG would improve the lookup experience in several concrete ways.

Semantic recall:

- Searching `clock gate` could still find passages that say `peripheral clock enable`.
- Searching `GPIO matrix input select` could find related register descriptions even if exact words differ.

Multi-document lookup:

- The system could search datasheet, TRM, application notes, errata, and vendor migration notes together.
- Results could be filtered by vendor, chip, document type, peripheral, page range, or alert status.

Context assembly:

- A retriever can collect the best chunks, nearby chunks, section heading path, table records, and alert records into one answer context.

Citation discipline:

- Every generated answer can carry `doc_id p.x-y`.
- Answers that depend on numeric or register table values can require sidecar/PDF verification.

Better interactive workflow:

- Instead of manually grepping files, a query command can return the top evidence bundle for a question.

For the current corpus size, this is an incremental workflow improvement, not a root-level capability jump. The root-level improvement already came from converting PDFs into structured, page-aware, table-aware artifacts.

## What RAG Would Not Fix

RAG does not solve parsing errors.

It will not automatically fix:

- ultra-wide pin/alternate-function matrix parsing
- register bit diagrams represented as images
- formula serialization failures
- empty table sidecars
- figure-like content misclassified as tables
- wrong OCR on scanned PDFs

For those cases, the right controls are still:

- `alerts.json`
- `document.html`
- `artifacts/`
- table sidecars
- original PDF page inspection
- later A/B testing with other parsers

## Recommended Landing Order

The recommended order is now intentionally conservative.

### Step 1: Keep Docling Conversion As The Mainline

No change needed to the core conversion architecture.

The current output shape is already suitable:

- `manifest.json`
- `chunks.jsonl`
- `sections.jsonl`
- `tables/`
- `artifacts/`
- `alerts.json`
- original PDF path and SHA-256

### Step 2: Try Existing Open-Source RAG Tools First

Before writing more custom code, test one or two existing RAG applications against the already processed manuals.

Good candidates:

- Kotaemon: a document-chat RAG UI with Docling available as a loader.
- RAGFlow: a larger RAG engine with document understanding, citations, multiple recall and re-ranking, and support for Docling/MinerU as parsing methods.
- Dify Knowledge: a general AI app platform with knowledge bases, retrieval testing, metadata, and configurable retrieval strategy.
- AnythingLLM: a quick local document-chat tool with broad model/vector DB support.
- Open WebUI with Docling plugin: useful if the final target is an existing local chat UI.

This experiment should answer:

- Does the tool preserve page citations?
- Can it ingest our `document.md` or original PDFs reliably?
- Can it expose source chunks clearly?
- Can it preserve or link to table sidecars?
- Can it surface `alerts.json` or equivalent parser-risk metadata?
- Can it run locally without making the workstation architecture worse?

If an existing tool is good enough, stop there.

### Step 3: Add A Local Retrieval Contract Only If Needed

Implement a small module or CLI that loads processed manuals and returns evidence records.

Suggested command shape:

```sh
docling/.venv/bin/python -m docling_bundle search \
  --manual manuals/processed/esp32-s3-technical-reference-manual-en \
  --query "I2C SCL low period register"
```

The output should be structured JSON, not prose:

```json
{
  "query": "I2C SCL low period register",
  "results": [
    {
      "doc_id": "esp32-s3-technical-reference-manual-en",
      "chunk_id": "esp32-s3-technical-reference-manual-en:1234",
      "score": 12.4,
      "heading_path": ["I2C Controller", "Register Summary"],
      "page_start": 842,
      "page_end": 843,
      "citation": "esp32-s3-technical-reference-manual-en p.842-843",
      "text": "...",
      "tables": [
        {
          "table_id": "esp32-s3-technical-reference-manual-en:table:0501",
          "csv_path": "tables/table_0501.csv",
          "html_path": "tables/table_0501.html"
        }
      ],
      "alerts": []
    }
  ]
}
```

This contract matters more than the first search algorithm. It defines what an AI assistant can safely consume.

### Step 4: Start With Lexical Search

The first implementation can be simple:

- load `chunks.jsonl`
- search `text` and `contextualized_text`
- support exact keywords and regex-like matching
- return page-aware chunks
- attach overlapping tables and alerts

Good candidates:

- SQLite FTS5
- Tantivy
- simple BM25 library
- in-memory lexical search for small corpora

This is enough to improve the current manual `rg` workflow while keeping the system debuggable.

### Step 5: Add Embeddings Only If Lexical Search Is Not Enough

After lexical search works, add local embeddings for semantic recall.

Implementation detail:

- Embed `contextualized_text`, not only raw `text`.
- Store chunk metadata next to the vector.
- Keep vector index rebuildable from `chunks.jsonl`.
- Do not treat the vector database as the source of truth.

Possible local index options:

- FAISS for a local file index
- SQLite plus vector extension if convenient
- Qdrant only if a service-style vector database becomes useful

The important rule:

```text
chunks.jsonl remains the rebuild source.
```

### Step 6: Add Hybrid Search And Context Packing Only At Larger Scale

For chip manuals, hybrid search is usually better than pure vector search.

Reason:

- Register names and bit names require exact matching.
- Natural-language descriptions benefit from semantic matching.

The search layer should combine:

- exact identifier matches
- BM25/lexical scores
- embedding scores
- metadata filters
- optional re-ranking

Then the context packer should attach:

- top chunks
- neighboring chunks when needed
- section heading path
- page citations
- related table records
- related alert records
- original PDF path

### Step 7: Enforce Answer Policy

Before using this system for engineering answers, define the policy the assistant must follow:

- Always cite page ranges.
- If `alert_count > 0`, check relevant alerts before trusting table-heavy results.
- If a result contains table sidecars, use them for numeric/register/electrical facts.
- If a result points to visual artifacts, inspect the artifact or original PDF page.
- For register values, bit definitions, pin mappings, timing limits, and electrical characteristics, cross-check the original PDF page before final engineering conclusions.

This policy is more important than which RAG framework is used.

### Step 8: Only Build Or Integrate More When There Is A Concrete Trigger

Use a full framework or deeper integration only if the project needs:

- multi-user UI
- persistent service deployment
- large multi-manual corpus management
- re-ranking pipelines
- agent tool integration
- query history
- document permissions
- distributed vector databases

Candidates may include:

- LlamaIndex
- LangChain
- Qdrant
- Milvus
- OpenSearch
- Elasticsearch

But those should be integration targets, not the foundation of the manual-processing design.

## Open-Source Practice Snapshot

The broader ecosystem confirms that Docling is usually used as the document ingestion/conversion layer, then connected to a RAG framework or application.

Observed patterns:

- Docling official examples integrate with LangChain, Haystack, and LlamaIndex.
- Those examples use Docling loaders/converters, `HybridChunker` or Docling-native node parsing, embedding models, vector stores such as Milvus, and a generation pipeline.
- Docling's own integrations page lists AI/RAG frameworks and applications such as LangChain, LlamaIndex, Haystack, Kotaemon, and Open WebUI.
- RAGFlow is a full RAG application with its own document engine, UI, APIs, storage services, retrieval, re-ranking, and agent features.
- Dify and AnythingLLM are app-level platforms for knowledge bases and document chat, not just parsing libraries.

This means Docling is not a half-finished RAG product. It is a document-preparation component. The "talk to my documents" layer is normally another tool.

The engineering mistake would be to reimplement a full RAG platform inside this repository.

## Direct Answer To The Implementation Question

Not necessarily.

The more accurate answer is:

```text
current state:
  convert PDFs into RAG-ready manual assets

recommended next action:
  try existing RAG applications against these assets

only if existing tools fail the embedded-manual evidence contract:
  add a small search/query adapter over chunks, sections, tables, and alerts

only if corpus scale or UX demands it:
  add embeddings, hybrid retrieval, context packing, or deeper framework integration
```

This sequencing keeps the architecture honest:

- Docling remains responsible for parsing and structured corpus generation.
- This repository remains responsible for embedded-manual-specific evidence quality.
- RAG software should be responsible for retrieval/runtime orchestration whenever it can preserve the evidence quality we need.

## Best-Practice Summary

Do not aim for:

```text
PDF -> summary -> model memory
```

Aim for:

```text
PDF -> structured corpus -> searchable evidence -> cited answer -> critical-value verification
```

For embedded development, that is the robust path.

## References

- RAG paper: https://arxiv.org/abs/2005.11401
- Docling chunking concepts: https://docling-project.github.io/docling/concepts/chunking/
- Docling RAG with LangChain example: https://docling-project.github.io/docling/examples/rag_langchain/
- Docling RAG with Haystack example: https://docling-project.github.io/docling/examples/rag_haystack/
- Docling RAG with LlamaIndex example: https://docling-project.github.io/docling/examples/rag_llamaindex/
- Docling Kotaemon integration: https://docling-project.github.io/docling/integrations/kotaemon/
- Docling Open WebUI integration: https://docling-project.github.io/docling/integrations/openwebui/
- RAGFlow: https://github.com/infiniflow/ragflow
- Dify Knowledge: https://docs.dify.ai/en/use-dify/knowledge/readme
- AnythingLLM: https://github.com/Mintplex-Labs/anything-llm
- Current manual-processing architecture: `docs/architecture/2026-04-12-docling-embedded-manual-processing.md`
