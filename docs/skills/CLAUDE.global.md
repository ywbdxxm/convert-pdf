# Global CLAUDE.md (user-level)

## Embedded / chip-manual tasks

When the user asks about **ESP32 / ESP32-S3 / ESP32-C3 / STM32 / RISC-V / MCU datasheets, TRMs, registers, pins, GPIO mux, peripherals, electrical characteristics, boot mode, clock trees**, or writes embedded firmware / HAL / drivers that reference specific chip identifiers:

**Invoke the `using-manual-bundles` skill before doing anything else.**

This skill enforces:
- Check `manuals/processed/docling_bundle/` in the current workspace first (before Espressif MCP / external docs / training data)
- Cite answers with `doc_id p.X` + `chunk_id` / `table_id` / `section_id`
- Consult `alerts.json` before trusting any content (regla 5: silent failure is the biggest antipattern)
- Fall back to `manuals/raw/<...>.pdf` when alerts flag the target, or to external docs only when the bundle doesn't cover it

Bundles are self-contained directories with `README.md` as the entry; `manifest.json` / `alerts.json` / `sections.jsonl` / `chunks.jsonl` / `tables.index.jsonl` / `cross_refs.jsonl` / `pages.index.jsonl` / `tables/*.csv` / `document.{md,json,html}` / `assets/` as structured data. See the skill for the full consumption flow and jq patterns.
