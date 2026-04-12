# Docling Batch Optimization Directions

Date: 2026-04-13

## Purpose

This document records how `docling_batch` should be understood now that the project has narrowed its mainline comparison to `Docling` and `OpenDataLoader PDF`.

The key clarification is:

> `docling_batch` is not a different parser from Docling. It is mostly a productized packaging layer on top of Docling's native APIs.

That means future changes to `docling_batch` should be judged as:

- helping agents read the generated folder more effectively
- reducing confusion between native Docling output and our custom packaging
- improving evidence visibility

and not as:

- building a new parser
- building a new RAG framework
- endlessly patching parse imperfections with fragile heuristics

## What `docling_batch` Actually Adds

Compared with plain Docling outputs, `docling_batch` currently adds:

- stable `doc_id` path layout
- `manifest.json`
- `chunks.jsonl`
- `sections.jsonl`
- `tables/*.csv` and `tables/*.html`
- `alerts.json`
- optional `_windows/` cache
- Markdown table-sidecar links
- some filtering, caption recovery, and alert heuristics

The underlying parser, chunker, and document export path still come from Docling:

- `DocumentConverter`
- `ThreadedStandardPdfPipeline`
- `DoclingDocument.save_as_json`
- `DoclingDocument.save_as_markdown`
- `DoclingDocument.save_as_html`
- `HybridChunker`
- `TableItem.export_to_dataframe/html/markdown`

So the user's intuition is basically correct:

> `docling_batch` is very close to "Docling native output plus some extra packaging and file-oriented convenience."

## Why Keep It At All

Even if it is not the final winner, `docling_batch` still has value:

- It is the current baseline already validated on real manuals.
- It gives a concrete example of what an agent-friendly output bundle can look like.
- It already surfaces some real failure modes via alerts and sidecars.
- It can act as a comparison point for whether external tools truly reduce custom code.

## Optimization Boundary

If `docling_batch` stays frozen, use it only as baseline.

If `docling_batch` is explicitly unfrozen, only make thin, high-value, file-oriented improvements.

### Allowed Directions

These all fit the current agentic file retrieval architecture.

#### 1. Page-Level Slices

Add page-oriented exports such as:

```text
pages/page_0027.md
pages/page_0027.json
```

Why:

- lets Codex jump directly to a page mentioned in a citation
- useful for hard pages such as wide tables and figure-heavy layouts
- avoids loading the entire document when only one page matters

#### 2. Folder Entrypoint

Add a generated top-level navigation file such as:

```text
README.generated.md
index.json
```

Why:

- gives the agent one obvious file to open first
- summarizes key assets and recommended reading order
- reduces directory guessing

Candidate contents:

- source PDF path
- page count
- table count
- alert count
- key paths
- quick-start instructions for agent lookup

#### 3. Quality Summary

Add a concise file such as:

```text
quality-summary.md
```

Why:

- summarizes the risk profile of a processed manual in one place
- highlights empty sidecars, image-fallback tables, formula issues, and similar concerns
- makes it easier for the agent to know when to distrust structure and return to the PDF

#### 4. Optional Hard-Page Images

Add page images only for selected pages:

- pages referenced by alerts
- user-requested pages
- known hard pages such as wide matrices

Why:

- improves verification for wide tables, register bit diagrams, timing diagrams, and figure-like tables
- avoids generating a full page-image corpus by default

This should stay opt-in or targeted, not become the default for every document.

#### 5. Native Chunk Comparison Export

Add an export that preserves Docling-native chunk output beside the current filtered custom chunk files.

Examples:

```text
chunks.native.jsonl
chunks.filtered.jsonl
```

Why:

- helps distinguish Docling behavior from our post-processing
- makes it easier to evaluate whether current filters help or harm retrieval
- reduces guesswork when comparing Docling to OpenDataLoader

#### 6. Heuristic Gating Or Removal

Current custom logic like:

- caption recovery
- Markdown image filtering
- noisy chunk filtering
- alert detection rules

should be easier to disable or separate.

Why:

- makes comparison against native Docling cleaner
- reduces accidental overfitting
- prevents hidden behavior from being mistaken for parser quality

The default direction should be toward simpler, more explicit behavior, not more heuristics.

## Disallowed Directions

These should not be built inside `docling_batch`.

### 1. Search / Retrieval / Vector Index

Do not add:

- lexical search engine
- vector DB
- embeddings
- reranking
- query rewriting
- answer assembly

Reason:

- that reopens the RAG/tooling path we deliberately cut off
- it does not improve file assets directly

### 2. More Fragile Parse-Healing Heuristics

Do not keep layering:

- caption inference hacks
- image/table reclassification guesses
- parser-specific post-fixes for every weird manual page

Reason:

- this becomes endless maintenance
- it hides the true parser behavior
- it recreates exactly the NIH path we backed away from

### 3. VLM Rescue Pipelines

Do not turn `docling_batch` into:

- page screenshot + VLM repair
- multimodal fallback orchestrator
- secondary parser router

Reason:

- too heavy
- too open-ended
- should only exist after a parser winner is chosen and a real gap remains

### 4. Multi-Tool Orchestration

Do not make `docling_batch` responsible for:

- running Marker
- running OpenDataLoader
- running MinerU
- normalizing all tools
- managing trial matrices

Reason:

- that belongs to evaluation workflow, not the Docling wrapper itself

### 5. UI / App Features

Do not add:

- document chat
- API server
- browser UI
- knowledge-base workflow

Reason:

- not part of the parser-output problem

## Recommended Use Going Forward

Treat `docling_batch` as one of two things:

### Option A: Frozen Baseline

Use it exactly as it is now for comparison against:

- Docling native output
- OpenDataLoader PDF local mode
- OpenDataLoader PDF hybrid mode

This is the safest path if external tools quickly outperform or match it.

### Option B: Thin Agent-Friendly Wrapper

If we later decide the Docling family remains the best parser path, keep `docling_batch` but reduce its ambition:

- preserve only file-navigation improvements
- expose native-vs-custom outputs clearly
- keep heuristics minimal and optional

This is the only acceptable "unfrozen" direction.

## Practical Decision Rule

Before making any future `docling_batch` change, ask:

1. Does this help Codex inspect the folder more directly?
2. Does this improve evidence visibility without hiding parser behavior?
3. Can this be explained as packaging rather than parser invention?
4. Would this still make sense if OpenDataLoader becomes the winner?

If the answer to any of these is "no", the change probably does not belong in `docling_batch`.
