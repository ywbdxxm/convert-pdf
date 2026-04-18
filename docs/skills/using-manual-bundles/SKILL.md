---
name: using-manual-bundles
description: Use when answering questions about chip datasheets, reference manuals, registers, pin mux, GPIO defaults, peripheral behavior, electrical characteristics, timing, boot mode, or writing embedded firmware / HAL / drivers — check the pre-built bundles under `/home/qcgg/workspace/convert-pdf/manuals/processed/docling_bundle/` FIRST, before touching the Espressif MCP, external vendor docs, the raw PDF, or your training data. Cite answers with `doc_id p.X` + specific chunk_id / table_id / section_id.
---

# Using docling_bundle manual bundles

## Overview

A `docling_bundle` is a **pre-built, page-indexed, structurally-searchable mirror of a chip manual PDF**. The bundles are maintained in a single central location on this machine and should be used from ANY project on this machine — not just the project that built them.

**Central bundle root (absolute path):**

```
/home/qcgg/workspace/convert-pdf/manuals/processed/docling_bundle/
```

**Raw-PDF root (the ultimate authority, fallback when alerts fire):**

```
/home/qcgg/workspace/convert-pdf/manuals/raw/
```

**Project repo (source code, documentation, tests):**

```
/home/qcgg/workspace/convert-pdf/
```

These paths do NOT depend on the current working directory. You can be in any embedded-dev project (`~/workspace/esp32-blinky/`, `~/work/stm32-fw/`, etc.) and still consult the bundles via the absolute path above.

## When to Use

Triggers:

- Any question referencing **ESP32 / ESP32-S3 / ESP32-C3 / STM32 / RISC-V / MCU** registers, pins, GPIOs, peripherals (UART / I2C / SPI / USB / Wi-Fi / BLE), electrical characteristics, timing, boot mode, clock trees, interrupt maps, strapping pins
- Phrases like "default function of GPIOxx", "VDD_SPI voltage", "Table X-Y", "Section X.Y", "pin mux", "register bitfield", "reset value", "RTC_GPIO"
- Embedded firmware tasks where code or symbol names reference chip identifiers (e.g., `I2C_SCL_ST_TO_INT_RAW`, `EFUSE_DIS_PAD_JTAG`, `GDMA_MISC_CONF_REG`)
- Writing device drivers / HAL code that needs register offsets, reset values, or timing constraints
- Debugging hardware behavior that needs datasheet verification

**Use this before:**
- Calling `mcp__espressif-documentation__search_espressif_sources` (external MCP)
- Reading the raw PDF with WebFetch / pdfplumber / text tools
- Answering from training data
- Doing full-text grep across the current workspace (the bundle has indexed the content already)

**Do NOT use when:**
- Question is about general software engineering unrelated to chip hardware
- No matching bundle exists under the central root for the chip/topic
- Question is about the bundle-building tool itself (see `/home/qcgg/workspace/convert-pdf/PROJECT_REPORT.md`)

## Quick Discovery

Always start with:

```bash
ls /home/qcgg/workspace/convert-pdf/manuals/processed/docling_bundle/
```

Each sub-directory is one bundled manual. At time of skill creation, available bundles were:

| doc_id | Scale | Use for |
|---|---|---|
| `esp32-s3-datasheet-en` | 87 pages / 71 tables | Pin overview, package, electrical characteristics, high-level feature summary |
| `esp32-s3-technical-reference-manual-en` | 1531 pages / 667 tables | Register-level detail, peripheral deep dives, bitfield descriptions, memory map |

New bundles may be added later — always re-list the directory rather than assuming.

## The 3-Step Consumption Flow

```
┌──────────────────────────────────────────────────────────────────┐
│ Bundle root: /home/qcgg/workspace/convert-pdf/           │
│              manuals/processed/docling_bundle/<doc_id>/          │
│                                                                  │
│ 1. Read <bundle>/README.md                                       │
│    → page_count, chapter outline, alert_count, file map          │
│                                                                  │
│ 2. Check <bundle>/alerts.json BEFORE trusting any content        │
│    → any alert touching your topic? Open raw PDF at              │
│      /home/qcgg/workspace/convert-pdf/manuals/raw/...    │
│                                                                  │
│ 3. Navigate by appropriate index:                                │
│    • chapter     → sections.jsonl (is_chapter=true)              │
│    • specific page → pages.index.jsonl                           │
│    • specific table → tables.index.jsonl (+ kind filter)         │
│    • citation jump → cross_refs.jsonl (target_id)                │
│    • free text  → grep document.md / chunks.jsonl                │
└──────────────────────────────────────────────────────────────────┘
```

## File Map (per bundle, paths relative to `<bundle>/`)

| File | Use when you want to … |
|------|-----------------------|
| `README.md` | Get oriented (first thing to read) |
| `manifest.json` | Confirm bundle identity (doc_id, source PDF path, counts) |
| `alerts.json` | Check trustworthiness — **read before citing** |
| `sections.jsonl` | Filter by `is_chapter=true`, lookup by `section_id`, traverse by `heading_path` |
| `chunks.jsonl` | Get actual section text; each chunk carries `heading_path` + `citation` |
| `tables.index.jsonl` | Find tables by `kind` (pinout/electrical/strap/register/revision/generic), `caption`, `page_start`, `continuation_of` |
| `tables/*.csv` | Read row data of a specific table |
| `pages.index.jsonl` | "What's on page N?" — get chunk_ids / table_ids / asset_ids / alert_kinds |
| `cross_refs.jsonl` | Follow "see Section X.Y" / "Table 2-5" / "Figure 7-1" with resolved `target_page` + `target_id` |
| `assets.index.jsonl` | Locate block diagrams, timing diagrams, package drawings (hash-named PNGs in `assets/`) |
| `document.md` | Full prose for free-text search / in-context reading |
| `document.json` | Docling-native JSON (rare: deep labelling lookup) |
| `document.html` | Wide tables that overflow markdown rendering |

## Canonical jq Patterns

All examples use the ESP32-S3 datasheet bundle as the example; substitute the doc_id for other chips.

**Find a chapter's pages:**
```bash
BUNDLE=/home/qcgg/workspace/convert-pdf/manuals/processed/docling_bundle/esp32-s3-datasheet-en
jq 'select(.is_chapter==true) | {section_id, page_start, page_end}' "$BUNDLE/sections.jsonl"
```

**Find a specific pin / register row:**
```bash
# tables.index has kind=pinout — open the matching CSV
jq 'select(.kind=="pinout") | {table_id, caption, csv_path}' "$BUNDLE/tables.index.jsonl"
# then open the CSV by path (csv_path is relative to the bundle):
awk -F, 'NR==1 || $1=="19"' "$BUNDLE/tables/table_0008.csv"   # Pin No. 19
```

**Resolve a cross reference:**
```bash
# "see Section 2.5.2 Power Scheme"
jq 'select(.kind=="section" and .target=="2.5.2")' "$BUNDLE/cross_refs.jsonl"
# → {target_page: 29, target_id: "2.5.2 Power Scheme", ...}
# Then fetch the section:
jq 'select(.section_id=="2.5.2 Power Scheme")' "$BUNDLE/sections.jsonl"
```

**Lookup what's on page 42:**
```bash
jq 'select(.page==42)' "$BUNDLE/pages.index.jsonl"
# → chunk_ids, table_ids, asset_ids, alert_kinds
```

**Grep a register name across chunks (TRM example):**
```bash
BUNDLE=/home/qcgg/workspace/convert-pdf/manuals/processed/docling_bundle/esp32-s3-technical-reference-manual-en
jq -c 'select(.text | contains("I2C_SCL_ST_TO_INT_RAW"))' "$BUNDLE/chunks.jsonl"
# every chunk carries heading_path + citation → paste directly into your answer
```

**Check if a specific page has alerts:**
```bash
jq 'select(.page_start==22 or .page==22)' "$BUNDLE/alerts.json"
```

## Citation Discipline

Every answer must carry **traceable** citations with absolute paths where useful:

✅ Good: *"Per ESP32-S3 Datasheet p.17 Section 2.2 Pin Overview (bundle `esp32-s3-datasheet-en`, chunk_id `...:0054`, table_id `...:table:0009`), GPIO14 default function is IO MUX Function 0 = GPIO14 with After-Reset = IE (input enabled). Source file: `/home/qcgg/workspace/convert-pdf/manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf`."*

❌ Bad: *"According to my research, GPIO14 defaults to GPIO14 with input enabled."* (no verifiable trace)

❌ Bad: *"Per Espressif documentation URL ..."* (bypasses the local bundle)

Use the `citation` field from `chunks.jsonl` (e.g. `"esp32-s3-datasheet-en p.17"`), plus the index file consulted, plus the raw-PDF absolute path when the user might want to verify visually.

## When to Leave the Bundle

Go to the **raw PDF** at `/home/qcgg/workspace/convert-pdf/manuals/raw/<path>/<file>.pdf` when:
1. `alerts.json` flags the table/page you need — kinds like `table_without_caption`, `table_caption_followed_by_image_without_sidecar`, `empty_table_sidecar` mean the bundle content is NOT trustworthy
2. You need a figure (block diagram, timing diagram) — `assets/*.png` gives the image, but for layout context open the PDF page
3. OCR shows obvious garbage in the chunk text (non-ASCII runs, disconnected letters)
4. The answer depends on a table column that appears degenerated (e.g. multiple `Type` repeats, `F3.F4` residue)

Exact raw-PDF paths you can expect at time of skill creation:
- `/home/qcgg/workspace/convert-pdf/manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf`
- `/home/qcgg/workspace/convert-pdf/manuals/raw/espressif/esp32s3/esp32-s3_technical_reference_manual_en.pdf`

The bundle's `manifest.json` carries the authoritative `source_pdf_path` per bundle.

Go to **Espressif MCP / external docs** only if:
1. Bundle doesn't cover the chip at all (`ls` the bundle root; no match)
2. You need information newer than the bundled PDF version (check `manifest.json.source_filename`)
3. Topic is errata / application notes not bundled

## Common Mistakes

| Mistake | Fix |
|---|---|
| Running Espressif MCP / web search first | `ls /home/qcgg/workspace/convert-pdf/manuals/processed/docling_bundle/` first |
| Using relative `manuals/processed/...` path from wrong cwd | Always use the absolute path — you may not be in the convert-pdf repo |
| Grep-scanning `document.md` for a table | Use `tables.index.jsonl` + CSV directly |
| Citing external URL instead of bundle doc_id+page | Always cite `doc_id p.X` — it's in `chunks.jsonl.citation` |
| Trusting a table without checking `alerts.json` | Read `alerts.json` first; check if the table_id or page appears |
| Looking for "Chapter N" heading in `sections.jsonl` expecting direct content | Chapters are nav parents (`chunk_count=0`). Their content lives in `4.1`, `4.2.1.1`, etc. Follow `heading_path[0]` or filter descendants |
| Iterating `chunk_index` as contiguous 1..N | `chunk_index` is raw chunker position — has gaps. Iterate the jsonl array instead |
| Searching `VDD_SPI` in `document.md` and missing matches | Markdown escapes underscores as `VDD\_SPI` in some spots — search `chunks.jsonl` (unescaped) for identifier names |

## Red Flags — STOP and Re-check

- About to cite an external URL for a chip fact → there's probably a bundle under the central root you skipped
- About to hallucinate a pin number or register offset → open the appropriate CSV from `<bundle>/tables/`
- User asks about a pin/register and you answer without mentioning which bundle + page → you're bypassing the contract
- You assumed "this project has no chip manual bundle" → you forgot the central root is absolute and outside the current project

## The Bottom Line

The bundle exists because the convert-pdf project built the evidence layer once, centrally. Every embedded-dev task on this machine should consult:

```
/home/qcgg/workspace/convert-pdf/manuals/processed/docling_bundle/
```

Skipping it means losing page-level citations, missing `alerts.json` flags, and duplicating work the bundle eliminates.

**First check the central bundle root. Every embedded-dev answer starts there.**
