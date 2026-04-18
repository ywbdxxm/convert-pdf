---
name: using-manual-bundles
description: Use when answering questions about chip datasheets, reference manuals, registers, pin mux, GPIO defaults, peripheral behavior, electrical characteristics, or embedded firmware tasks — before touching the Espressif MCP, external vendor docs, or the raw PDF, check whether a pre-built `manuals/processed/docling_bundle/<doc_id>/` exists in the workspace and use it as the primary source with page-level citations.
---

# Using docling_bundle manual bundles

## Overview

A `docling_bundle` is a **pre-built, page-indexed, structurally-searchable mirror of a chip manual PDF**. When it exists in a workspace, it is the authoritative citation source — not external docs, not the raw PDF text (which loses structure), not your training data.

The bundle's contract is:
- Every answer can be cited by `doc_id p.X` + a specific `chunk_id` / `table_id` / `section_id`
- `alerts.json` tells you upfront which pages / tables are NOT trustworthy — for those, open the raw PDF in `manuals/raw/`
- Structured indices (`sections.jsonl` / `tables.index.jsonl` / `cross_refs.jsonl` / `pages.index.jsonl`) let you jump by chapter / page / table / citation in one `jq` call instead of grep-scanning prose

## When to Use

Triggers:

- Any question referencing **ESP32 / ESP32-S3 / ESP32-C3 / STM32 / RISC-V / MCU** registers, pins, GPIOs, peripherals (UART / I2C / SPI / USB / Wi-Fi / BLE), electrical characteristics, timing, boot mode, clock trees, interrupt maps
- Phrases like "default function of GPIOxx", "VDD_SPI voltage", "Table X-Y", "Section X.Y", "strapping pin", "pin mux", "register bitfield"
- Embedded firmware tasks where the code comments / symbol names reference chip identifiers (e.g., `I2C_SCL_ST_TO_INT_RAW`, `EFUSE_DIS_PAD_JTAG`)
- Writing device drivers / HAL code that needs register offsets, reset values, or timing constraints
- Debugging hardware behavior that needs datasheet verification

**Use this before:**
- Calling `mcp__espressif-documentation__search_espressif_sources` (external MCP)
- Reading the raw PDF directly with WebFetch / pdfplumber
- Answering from training data
- Doing full-text grep across the workspace

**Do NOT use when:**
- Question is about general software engineering unrelated to chip hardware
- Workspace has no `manuals/processed/docling_bundle/` directory
- Question is about tooling that builds the bundle itself (see project README instead)

## Quick Discovery

Before answering any hardware/datasheet question, run:

```bash
ls manuals/processed/docling_bundle/ 2>/dev/null
```

If the directory exists, **every sub-directory is one bundled manual** (e.g. `esp32-s3-datasheet-en/`, `esp32-s3-technical-reference-manual-en/`). Pick the one matching the chip + topic (datasheet = overview/pins/electrical; technical reference manual = registers/peripherals deep dive) and read its `README.md` first.

## The 3-Step Consumption Flow

```
┌──────────────────────────────────────────────────────┐
│ 1. Read <bundle>/README.md                           │
│    → get page_count, chapter outline, alert_count    │
│                                                      │
│ 2. Check alerts.json BEFORE trusting any content     │
│    → any alert touching your topic? Open raw PDF.    │
│                                                      │
│ 3. Navigate by appropriate index:                    │
│    • chapter     → sections.jsonl (is_chapter=true)  │
│    • specific page → pages.index.jsonl               │
│    • specific table → tables.index.jsonl (+kind)     │
│    • citation jump → cross_refs.jsonl (target_id)    │
│    • free text  → grep document.md / chunks.jsonl    │
└──────────────────────────────────────────────────────┘
```

## File Map (per bundle)

| File | Use when you want to … |
|------|-----------------------|
| `README.md` | Get oriented (first thing to read) |
| `manifest.json` | Confirm bundle identity (doc_id, source PDF path, counts) |
| `alerts.json` | Check trustworthiness — **read before citing** |
| `sections.jsonl` | Filter by `is_chapter=true`, lookup by `section_id`, traverse by `heading_path` |
| `chunks.jsonl` | Get actual section text; each chunk carries `heading_path` + `citation` |
| `tables.index.jsonl` | Find tables by `kind` (pinout/electrical/strap/register/revision/generic), `caption`, `page_start`, or `continuation_of` |
| `tables/*.csv` | Read row data of a specific table |
| `pages.index.jsonl` | "What's on page N?" — get chunk_ids / table_ids / asset_ids / alert_kinds |
| `cross_refs.jsonl` | Follow "see Section X.Y" / "Table 2-5" / "Figure 7-1" with resolved `target_page` + `target_id` |
| `assets.index.jsonl` | Locate block diagrams, timing diagrams, package drawings (hash-named PNGs in `assets/`) |
| `document.md` | Full prose for free-text search / in-context reading |
| `document.json` | Docling-native JSON (rare: deep labelling lookup) |
| `document.html` | Wide tables that overflow markdown rendering |

## Canonical jq Patterns

**Find a chapter's pages:**
```bash
jq 'select(.is_chapter==true) | {section_id, page_start, page_end}' sections.jsonl
```

**Find a specific pin / register row:**
```bash
# tables.index has kind=pinout — open the matching CSV
jq 'select(.kind=="pinout") | {table_id, caption, csv_path}' tables.index.jsonl
# then:
awk -F, 'NR==1 || $1=="19"' tables/table_0008.csv   # Pin No. 19
```

**Resolve a cross reference:**
```bash
# "see Section 2.5.2 Power Scheme"
jq 'select(.kind=="section" and .target=="2.5.2")' cross_refs.jsonl
# → {target_page: 29, target_id: "2.5.2 Power Scheme", ...}
# Then fetch the section:
jq 'select(.section_id=="2.5.2 Power Scheme")' sections.jsonl
```

**Lookup what's on page 42:**
```bash
jq 'select(.page==42)' pages.index.jsonl
# → chunk_ids, table_ids, asset_ids, alert_kinds
```

**Grep a register name across chunks:**
```bash
jq -c 'select(.text | contains("I2C_SCL_ST_TO_INT_RAW"))' chunks.jsonl
# every chunk carries heading_path + citation → paste directly into your answer
```

**Check if a specific page has alerts:**
```bash
jq 'select(.page_start==22 or .page==22)' alerts.json
```

## Citation Discipline

Every answer must carry **traceable** citations:

✅ Good: *"Per ESP32-S3 Datasheet p.17 Section 2.2 Pin Overview (bundle `esp32-s3-datasheet-en`, chunk `:0054`), GPIO14 default function is IO MUX Function 0 = GPIO14 with After-Reset = IE (input enabled)."*

❌ Bad: *"According to my research, GPIO14 defaults to GPIO14 with input enabled."* (no verifiable trace)

❌ Bad: *"Per Espressif documentation URL ..."* (bypasses the local bundle)

Use `citation` field from chunks, or `doc_id p.X-Y` from `citation`, plus the index file name you consulted.

## When to Leave the Bundle

Go to `manuals/raw/<...>.pdf` (source PDF) when:
1. `alerts.json` flags the table/page you need — alert kinds like `table_without_caption`, `table_caption_followed_by_image_without_sidecar`, `empty_table_sidecar` mean the bundle content is NOT trustworthy
2. You need a figure (block diagram, timing diagram) — `assets/*.png` gives you the image, but for layout context open the PDF page
3. OCR shows obvious garbage in the chunk text (non-ASCII runs, disconnected letters)
4. The answer depends on a table column that appears degenerated (e.g. multiple `Type` repeats, `F3.F4` residue)

Go to the **Espressif MCP / external docs** only if:
1. Bundle doesn't cover the chip at all
2. You need information from a version newer than the bundled PDF
3. The topic is errata / application notes not bundled

## Common Mistakes

| Mistake | Fix |
|---|---|
| Running Espressif MCP / web search first | Check `manuals/processed/docling_bundle/` first |
| Grep-scanning `document.md` for a table | Use `tables.index.jsonl` + CSV directly |
| Citing external URL instead of bundle doc_id+page | Always cite `doc_id p.X` — it's in `chunks.jsonl.citation` |
| Trusting a table without checking `alerts.json` | Read `alerts.json` first; check if the table_id or page appears |
| Looking for "Chapter N" heading in `sections.jsonl` expecting direct content | Chapters are nav parents (`chunk_count=0`). Their content lives in `4.1`, `4.2.1.1`, etc. — follow `heading_path[0]` |
| Iterating `chunk_index` as contiguous 1..N | `chunk_index` is raw chunker position — has gaps. Iterate the jsonl array instead |
| Searching `VDD_SPI` in `document.md` and missing 16 matches | Markdown escapes underscores as `VDD\_SPI` in some spots — search `chunks.jsonl` (unescaped) for identifier names |

## Red Flags — STOP and Re-check

- About to cite an external URL for a chip fact → there's probably a bundle you skipped
- About to hallucinate a pin number or register offset → open the appropriate CSV
- User asks about a pin/register and you answer without mentioning which bundle + page → you're bypassing the contract
- You said "the workspace is unrelated to X" without running `ls manuals/processed/docling_bundle/` → the workspace IS the bundle in most embedded-dev sessions

## The Bottom Line

The bundle exists because the project's hard work already built the evidence layer. Skipping it means:
- Losing page-level citations the user expects
- Missing `alerts.json` flags and silently returning bad data
- Duplicating work the bundle was designed to eliminate

**First check `manuals/processed/docling_bundle/`. Every embedded-dev answer starts there.**
