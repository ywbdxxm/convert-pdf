---
name: using-manual-bundles
description: Use when answering questions about chip datasheets, technical reference manuals (TRM), registers, pin mux, GPIO defaults, peripheral behavior, electrical characteristics, timing, boot mode, interrupt maps, clock trees — or when writing embedded firmware / HAL / driver / bring-up code that references chip identifiers (e.g. `GPIO14`, `VDD_SPI`, `I2C_SCL_ST_TO_INT_RAW`, `EFUSE_DIS_PAD_JTAG`) — before consulting any external MCP, web docs, raw PDF, or training data.
---

# Using docling_bundle manual bundles

## Overview

A `docling_bundle` is a **pre-built, page-indexed, 4-axis-navigable mirror of a chip manual PDF**, paired with a **surfaced-failure contract** (`alerts.json` explicitly lists every table / page the bundle layer could not perfectly parse). The bundles are authoritative for the PDFs they cover; use them before any external lookup.

**Central bundle root (absolute, cwd-independent):**

```
/home/qcgg/workspace/convert-pdf/manuals/processed/docling_bundle/
```

**Raw-PDF root (ultimate authority; fallback when `alerts.json` fires):**

```
/home/qcgg/workspace/convert-pdf/manuals/raw/
```

These paths work from any embedded-dev project (`~/workspace/esp32-blinky/`, `~/work/stm32-fw/`, …). Never use a relative path — you may not be inside the `convert-pdf` repo.

## Why this bundle beats the alternatives

| Approach | Problem |
|---|---|
| Dump full PDF to LLM | Context blows up; OCR errors become "facts"; no verifiable page-level citation |
| RAG over PDF | Vector hit without chapter / page / table context; not re-verifiable |
| Docling raw output | Flat markdown, no reverse index, no trust signal |
| Espressif MCP / web first | External network call; vendor site may not match the exact PDF revision you're working against |
| Grep the raw PDF | `pdftotext` breaks tables; markdown-escaped identifiers (`VDD\_SPI`) go missing |

What the bundle layer adds on top of Docling:

- **4-axis navigation** — every question maps to an index, `O(index lookup)` not full-text scan:
  - page → `pages.index.jsonl`
  - section / chapter → `sections.jsonl`
  - table → `tables.index.jsonl` (+ `kind` filter: pinout / electrical / strap / register / revision / generic)
  - cross-reference → `cross_refs.jsonl` (resolved `target_page` + `target_id`)
- **Heading-path breadcrumbs on every chunk** — each `chunks.jsonl` record carries its full ancestor chain (`4 Functional Description → 4.1 System → 4.1.3 System Components → 4.1.3.5 Power Management Unit (PMU)`). Answers always know "which chapter, which section".
- **Ready-to-paste `citation` field** — every chunk and every table record already contains `"doc_id p.X-Y"`. No citation assembly by hand.
- **One-hop cross-references** — 43/47 refs on datasheet and ~98% on TRM come with `target_id` pointing directly at a `section_id` / `table_id`. One jq call to follow.
- **Nav-parent chapter roll-ups** — chapter entries in `sections.jsonl` (`chunk_count=0, is_chapter=true`) give you `page_start / page_end / table_ids` for the entire chapter in one record.
- **Surfaced failure (`alerts.json`)** — tables or pages the bundle layer can't verify are listed explicitly; check before trusting a table. **Silent failure is not tolerated**: post-Phase-60, footer noise (e.g. "Submit Documentation Feedback") is stripped from mixed chunks, not discarded whole; empty-after-strip chunks still drop, but never by accident.
- **CSV sidecar per table** — `tables/table_NNNN.csv` gives machine-readable rows; `caption` + `kind` + `continuation_of` make filtering trivial.
- **Three canonical doc views** — `document.md` (grep / read), `document.html` (wide-table visual verify), `document.json` (Docling-native, for deep label / prov lookups).

## When to Use

Triggers:

- Any question referencing **ESP32 / ESP32-S3 / ESP32-C3 / STM32 / RISC-V / MCU** registers, pins, GPIOs, peripherals (UART / I2C / SPI / USB / Wi-Fi / BLE), electrical characteristics, timing, boot mode, clock trees, interrupt maps, strapping pins
- Phrases: "default function of GPIOxx", "VDD_SPI voltage", "Table X-Y", "Section X.Y", "pin mux", "register bitfield", "reset value", "RTC_GPIO"
- Embedded firmware / HAL / driver / bring-up tasks where symbol names reference chip identifiers (e.g. `I2C_SCL_ST_TO_INT_RAW`, `EFUSE_DIS_PAD_JTAG`, `GDMA_MISC_CONF_REG`)
- Debugging hardware behavior that needs datasheet verification

**Use this BEFORE:**

- Calling `mcp__espressif-documentation__search_espressif_sources`
- Reading the raw PDF via WebFetch / pdfplumber / text tools
- Answering from training data
- Full-text grep across the workspace

**Do NOT use when:**

- Generic software question unrelated to chip hardware
- No bundle exists under the central root for the chip/topic
- Question is about the bundle-building tool itself (see `/home/qcgg/workspace/convert-pdf/PROJECT_REPORT.md`)

## Quick Discovery

Always list first:

```bash
ls /home/qcgg/workspace/convert-pdf/manuals/processed/docling_bundle/
```

Available bundles (verified 2026-04-19, Phase 60):

| doc_id | Scale | Best for |
|---|---|---|
| `esp32-s3-datasheet-en` | 87 pages · 145 sections · 339 chunks · 71 tables · 3 alerts | Pin overview, package, electrical characteristics, high-level feature summary |
| `esp32-s3-technical-reference-manual-en` | 1531 pages · 1663 sections · 3793 chunks · 667 tables · 380 alerts | Register-level detail, peripheral deep dives, bitfield descriptions, memory map |

Always re-list — new bundles may be added.

## The 3-Step Consumption Flow

```
┌──────────────────────────────────────────────────────────────────┐
│ Bundle root: /home/qcgg/workspace/convert-pdf/           │
│              manuals/processed/docling_bundle/<doc_id>/          │
│                                                                  │
│ 1. Read <bundle>/README.md                                       │
│    → page_count, chapter outline, alert summary, file map        │
│                                                                  │
│ 2. Check <bundle>/alerts.json BEFORE trusting any content        │
│    → any alert touching your topic? Fall back to raw PDF at      │
│      /home/qcgg/workspace/convert-pdf/manuals/raw/...    │
│                                                                  │
│ 3. Navigate on the right axis:                                   │
│    • chapter / section → sections.jsonl                          │
│    • specific page     → pages.index.jsonl                       │
│    • specific table    → tables.index.jsonl (+ kind filter)      │
│    • citation jump     → cross_refs.jsonl (target_id)            │
│    • identifier grep   → chunks.jsonl (unescaped text)           │
│    • prose search      → document.md                             │
└──────────────────────────────────────────────────────────────────┘
```

## File Map (paths relative to `<bundle>/`)

| File | Use when you want to … |
|------|-----------------------|
| `README.md` | Get oriented — first file to open |
| `manifest.json` | Confirm bundle identity (`doc_id`, `source_pdf_path`, counts) |
| `alerts.json` | Check trustworthiness — **read before citing** |
| `sections.jsonl` | Filter by `is_chapter=true`; lookup by `section_id`; use **nav parents** (`chunk_count=0, is_chapter=true`) for chapter-level aggregate queries ("what does Chapter N cover") |
| `chunks.jsonl` | Get section text; each record carries `text`, `contextualized_text` (= `heading_path` joined + `text`, great for identifier grep), full `heading_path` breadcrumb, ready-to-paste `citation` |
| `tables.index.jsonl` | Find tables by `kind`, `caption`, `page_start`, `continuation_of` |
| `tables/*.csv` | Read row data of a specific table |
| `pages.index.jsonl` | "What's on page N?" — `chunk_ids / table_ids / asset_ids / alert_kinds`. **No `section_ids` on this index** — derive via any chunk_id → `chunks.jsonl.section_id` (or via `sections.jsonl.page_start/page_end` range filter) |
| `cross_refs.jsonl` | Follow "see Section X.Y" / "Table 2-5" / "Figure 7-1" with resolved `target_page` + `target_id` (one hop to target record). **`kind=figure` records have `target_page` but NO `target_id`** — figures have no global id, so jump via `assets.index.jsonl` (caption / page match) or open the raw PDF |
| `assets.index.jsonl` | Locate block diagrams, timing diagrams, package drawings (hash-named PNGs in `assets/`) |
| `document.md` | Full prose for free-text search / in-context reading |
| `document.json` | Docling-native JSON (rare: deep labelling lookup) |
| `document.html` | Wide tables that overflow markdown rendering |

## Typical Questions → Minimum Steps

Pin one of these recipes instead of grepping everything.

| Question | Steps | Method |
|---|---|---|
| "What does GPIO14 default to?" | 2 | `tables.index filter kind=pinout` → open matching CSV → find row |
| "VDD_SPI electrical characteristics?" | 2 | `tables.index filter kind=electrical` → open CSV |
| "Section 4.1.3.5 full text?" | 2 | `sections.jsonl filter section_id` → iterate `chunk_ids` in `chunks.jsonl` |
| "What does Chapter 4 cover (pages + tables)?" | 1 | `sections.jsonl filter is_chapter=true and section_id="4 …"` — nav-parent record has `page_start / page_end / table_ids` |
| "Who references Table 2-5?" | 1 | `cross_refs.jsonl filter target_id=<table_id>` |
| "Where is the block diagram?" | 1-2 | Grep `document.md` for caption → `assets.index` reverse lookup (or `pages.index filter page=N`) |
| "Meaning of `I2C_SCL_ST_TO_INT_RAW`?" | 1 | `jq 'select(.text \| contains("<REG>"))' chunks.jsonl` — record gives heading_path + citation |
| "Is this table trustworthy?" | 1 | `alerts.json filter table_id=<id>` — if listed, fall back to raw PDF |
| "Boot strapping pin defaults?" | 2 | `tables.index filter kind=strap` → CSV |

## Always Query with Bash (jq / awk / grep)

Every bundle file is JSONL, JSON, or CSV — **every query is a one-line Bash pipe**. Do **NOT** write a Python script or `import pandas` / `import json` to consume the bundle. Python adds subprocess overhead, burns context on boilerplate, and hides the retrieval path from the user. `jq 'select(…)'` and `awk -F, '$N=="X"'` cover 99% of real queries; `grep` + `head` cover the rest. Reach for Python only if you're post-processing 100k+ records into a derived artifact that will itself be committed — which is never the case for Q&A.

## Canonical jq Patterns

```bash
BUNDLE=/home/qcgg/workspace/convert-pdf/manuals/processed/docling_bundle/esp32-s3-datasheet-en
```

**Chapter list:**
```bash
jq 'select(.is_chapter==true) | {section_id, page_start, page_end}' "$BUNDLE/sections.jsonl"
```

**Chapter roll-up (one record → everything Chapter N covers):**
```bash
jq 'select(.section_id=="4 Functional Description")' "$BUNDLE/sections.jsonl"
# → page_start, page_end, table_ids — no need to walk descendants
```

**Pin / register row:**
```bash
jq 'select(.kind=="pinout") | {table_id, caption, csv_path}' "$BUNDLE/tables.index.jsonl"
awk -F, 'NR==1 || $1=="19"' "$BUNDLE/tables/table_0008.csv"   # Pin No. 19
```

**Resolve "see Section 2.5.2":**
```bash
jq 'select(.kind=="section" and .target=="2.5.2")' "$BUNDLE/cross_refs.jsonl"
# → {target_page: 29, target_id: "2.5.2 Power Scheme", ...}
jq 'select(.section_id=="2.5.2 Power Scheme")' "$BUNDLE/sections.jsonl"
```

**What's on page 42:**
```bash
jq 'select(.page==42)' "$BUNDLE/pages.index.jsonl"
```

**Grep an identifier (TRM example) — prefer `contextualized_text`:**
```bash
BUNDLE=/home/qcgg/workspace/convert-pdf/manuals/processed/docling_bundle/esp32-s3-technical-reference-manual-en

# Preferred: contextualized_text = heading_path + text joined, so the match
# record already carries chapter/section context — no second lookup needed.
jq -c 'select(.contextualized_text | contains("I2C_SCL_ST_TO_INT_RAW"))' "$BUNDLE/chunks.jsonl"

# Fallback: plain text if you only want hits in prose (not heading).
jq -c 'select(.text | contains("I2C_SCL_ST_TO_INT_RAW"))' "$BUNDLE/chunks.jsonl"
# every chunk carries heading_path + citation → paste directly
```

**Resolve "see Figure 7-1" (figures have target_page but no target_id):**
```bash
jq 'select(.kind=="figure" and .target=="7-1")' "$BUNDLE/cross_refs.jsonl"
# → {target_page: 77, raw: "see Figure 7-1", source_chunk_id: ...}
# target_id is NOT populated for figures — jump via assets.index:
jq 'select(.page_start==77 or .page==77)' "$BUNDLE/assets.index.jsonl"
```

**Check page for alerts:**
```bash
jq 'select(.page_start==22 or .page==22)' "$BUNDLE/alerts.json"
```

## Citation Discipline

Every answer must carry a **traceable** citation with absolute paths where useful:

✅ Good: *"Per ESP32-S3 Datasheet p.17 Section 2.2 Pin Overview (bundle `esp32-s3-datasheet-en`, chunk_id `…:0054`, table_id `…:table:0009`), GPIO14 default function is IO MUX Function 0 = GPIO14 with After-Reset = IE (input enabled). Source: `/home/qcgg/workspace/convert-pdf/manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf`."*

❌ Bad: *"According to my research, GPIO14 defaults to GPIO14 with input enabled."*

❌ Bad: *"Per Espressif documentation URL …"*

Use the `citation` field from `chunks.jsonl` (e.g. `"esp32-s3-datasheet-en p.17"`), name the index file consulted, and add the raw-PDF absolute path (from `manifest.json.source_pdf_path`) when the user might want to verify visually.

## When to Leave the Bundle

Go to the **raw PDF** (absolute path in `manifest.json.source_pdf_path`) when:

1. `alerts.json` flags the table/page — kinds like `table_without_caption`, `table_caption_followed_by_image_without_sidecar`, `empty_table_sidecar` mean bundle content at that location is NOT trustworthy
2. You need a figure — `assets/*.png` gives the image; the PDF gives layout context
3. OCR garbage in chunk text (non-ASCII runs, disconnected letters)
4. A table column is degenerate (`Type.Type` repeats, `F3.F4` residue)

Current raw-PDF absolute paths:

- `/home/qcgg/workspace/convert-pdf/manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf`
- `/home/qcgg/workspace/convert-pdf/manuals/raw/espressif/esp32s3/esp32-s3_technical_reference_manual_en.pdf`

Go to **Espressif MCP / external docs** only if:

1. Bundle doesn't cover the chip at all (`ls` root; no match)
2. Information newer than bundled PDF revision (check `manifest.json.source_filename`)
3. Errata / application notes not in the bundle

## Common Mistakes

| Mistake | Fix |
|---|---|
| Running Espressif MCP / web search first | `ls /home/qcgg/workspace/convert-pdf/manuals/processed/docling_bundle/` first |
| Using relative `manuals/processed/…` path from wrong cwd | Always use the absolute path |
| Grep-scanning `document.md` for a table | Use `tables.index.jsonl` + CSV directly |
| Grep `document.md` for `VDD_SPI` / register name and missing hits | Markdown escapes underscores (`VDD\_SPI` / `I2C\_SCL…`). Grep `chunks.jsonl` (unescaped identifiers) |
| Citing external URL instead of bundle doc_id+page | Always cite `doc_id p.X` — it's in `chunks.jsonl.citation` |
| Trusting a table without checking `alerts.json` | Read `alerts.json` first; check if the table_id or page appears |
| Looking for chapter content via `section_id="Chapter N"` | Chapters are nav parents with `chunk_count=0`. Use nav parent for roll-ups (`page_start / page_end / table_ids`); descend into `4.1`, `4.2.1.1`, … for prose |
| Iterating `chunk_index` as contiguous 1..N | `chunk_index` is raw chunker position — has gaps. Iterate the jsonl array position instead |
| Assuming "the chunk might have been silently dropped" | Post-Phase-60, no chunk is silently dropped. If expected content is missing, check `alerts.json` (surfaced flag) first, then raw PDF |
| Looking for `target_id` on Figure cross-refs | `kind=figure` records have `target_page` only; the `target_id` key is **absent** (not null) — jump via `assets.index.jsonl` (page / caption match) or open the raw PDF |
| Looking for `section_ids` on `pages.index.jsonl` | That field is not on the page index. Derive via any `chunk_id` → `chunks.jsonl.section_id`, or via `sections.jsonl` filtered by `.page_start<=N and .page_end>=N` |
| Writing a Python script / `import json` / `pandas` to read the bundle | Use `jq` / `awk` / `grep` one-liners. Python adds subprocess overhead, burns context on boilerplate, and hides the retrieval path. The bundle was designed for Bash consumption |
| Grepping only `.text` for a register identifier and missing matches that live in a heading | Grep `.contextualized_text` (= heading_path joined + text) — it catches both prose and heading-level hits in one pass |

## Red Flags — STOP and Re-check

- About to cite an external URL for a chip fact → there's a bundle under the central root you skipped
- About to hallucinate a pin number or register offset → open the right CSV from `<bundle>/tables/`
- You answered a pin / register question without naming which bundle + page → you're bypassing the citation contract
- You assumed "this project has no chip manual bundle" → central root is absolute, outside the current project

## The Bottom Line

```
/home/qcgg/workspace/convert-pdf/manuals/processed/docling_bundle/
```

This central root holds the **only structurally-validated, page-cited, surfaced-failure-marked copy** of the ESP32-S3 datasheet + TRM on this machine. Every embedded-dev answer on this machine starts there:

1. `ls` the root
2. Read `README.md` of the matching bundle
3. Check `alerts.json`
4. Query by the right axis (section / page / table / cross-ref / identifier)
5. Cite with `doc_id p.X` + chunk_id / table_id / section_id

Skipping means losing page-level citations, missing `alerts.json` flags, and duplicating work the bundle already did.
