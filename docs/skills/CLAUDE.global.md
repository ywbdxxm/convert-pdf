# Global CLAUDE.md (user-level)

## Embedded / chip-manual tasks

When the user asks about **ESP32 / ESP32-S3 / ESP32-C3 / MCU datasheets, TRMs, registers, pins, GPIO mux, peripherals, electrical characteristics, boot mode, clock trees, timing, strapping pins**, or writes embedded firmware / HAL / drivers that reference specific chip identifiers:

**Invoke the `using-manual-bundles` skill before doing anything else.**

The skill points you at a **central bundle root on this machine** (not the current project's directory):

```
Bundles:  /home/qcgg/workspace/convert-pdf/manuals/processed/docling_bundle/
Raw PDFs: /home/qcgg/workspace/convert-pdf/manuals/raw/
Project:  /home/qcgg/workspace/convert-pdf/
```

These paths are absolute — they work from any embedded-dev project on this machine (e.g. `~/workspace/esp32-blinky/`, `~/work/stm32-fw/`). Do **not** assume the bundle lives under the current working directory.

The skill enforces:
- `ls /home/qcgg/workspace/convert-pdf/manuals/processed/docling_bundle/` FIRST (before Espressif MCP / external docs / training data)
- Cite answers with `doc_id p.X` + `chunk_id` / `table_id` / `section_id`
- Consult `alerts.json` before trusting any content (silent failure is the biggest antipattern, per `/home/qcgg/workspace/convert-pdf/开发要求.md` rule 5)
- Fall back to `/home/qcgg/workspace/convert-pdf/manuals/raw/<path>/<file>.pdf` when alerts flag the target; fall back to external docs only when the bundle doesn't cover the chip at all

Bundles are self-contained directories with `README.md` as the entry; `manifest.json` / `alerts.json` / `sections.jsonl` / `chunks.jsonl` / `tables.index.jsonl` / `cross_refs.jsonl` / `pages.index.jsonl` / `tables/*.csv` / `document.{md,json,html}` / `assets/` as structured data. See the skill for the full consumption flow and jq patterns.
