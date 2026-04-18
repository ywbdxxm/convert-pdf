# Phase 56 — docling_bundle depth audit fixes

Date: 2026-04-18
Scope: `docling_bundle` only
Driving principle: `开发要求.md` — "agent 实际查阅 bundle 的体验" + Robustness Principle ("改动对所有 PDF 普遍适用，不为单一 datasheet 过拟合")

## Context

Phase 55 fixed one narrow issue (Unicode-bullet heading filter). Re-audit against the ESP32-S3 datasheet bundle surfaced four more issues that are (a) clearly impacting agent usability, (b) universal across vendors, and (c) low/medium risk of overfitting. Several other issues were identified but deliberately out of scope — see "Explicitly out of scope" at the bottom.

### Findings this spec addresses

| Tag | Finding | Usability impact |
|-----|---------|------------------|
| A | Every chunk's `heading_path` is depth 1 (just the immediate heading). Agents doing semantic / keyword search lose chapter and mid-level section context. | **Highest** — every chunk is affected |
| C | `tables.index.jsonl` has `rows: null` on all 71 tables. Dead schema. | Low-medium — agents doing table triage can't filter by size |
| D | TOC tables (`is_toc: true`) have garbage `columns` (`["0","1","2"]` or row-1 data). Misleading field. | Low — already filterable via `is_toc`, but footgun remains |
| G | Markdown has 14 standalone `Cont'd on next page` / `cont'd from previous page` paragraph lines between continuation tables. Clutters reading view. | Low — readable but visually noisy |

### Explicitly out of scope (reasons in findings.md §7b)

- Non-numbered bold sub-labels (`CPU Clock`, `General Features`, …) as level-1 TOC anchors — level reassignment is too risky because front-matter legitimately uses level-1 non-numbered headings.
- Glossary terms promoted to individual headings — detection rule is vendor-specific.
- Reducing tiny sections (55% of sections have ≤1 chunk) — aggregation would destroy fine-grained navigation that agents need for peripheral pages.
- Uncaptioned-table columns mangled by Docling MultiIndex flatten — already surfaced via `alerts.json` per 开发要求.md rule 5.

---

## Fix A — heading breadcrumbs

### Current behavior

In `docling_bundle/indexing.py:build_chunk_record`:

```python
headings = list(getattr(chunk.meta, "headings", None) or [])
# → always length 1 in observed output
```

A chunk inside section `4.1.3.1 IO MUX and GPIO Matrix` records only
`heading_path = ["4.1.3.1 IO MUX and GPIO Matrix"]`. Chapter (`4 Functional Description`) and mid-level parents (`4.1 System`, `4.1.3 System Components`) are lost.

### New behavior

Each chunk's `heading_path` becomes the full ancestor chain ending at the immediate heading, built from `doc.iterate_items()` in document order. `section_id` remains the leaf (last element of `heading_path`) — no change in grouping semantics.

Example:

```json
// before
{"chunk_id": "...:0143", "heading_path": ["4.1.3.1 IO MUX and GPIO Matrix"], "section_id": "4.1.3.1 IO MUX and GPIO Matrix"}

// after
{"chunk_id": "...:0143",
 "heading_path": ["4 Functional Description", "4.1 System", "4.1.3 System Components", "4.1.3.1 IO MUX and GPIO Matrix"],
 "section_id": "4.1.3.1 IO MUX and GPIO Matrix"}
```

### Algorithm

New helper `build_doc_item_lineages(doc) -> dict[int, list[str]]`:

1. Walk `doc.iterate_items()` in document order.
2. Maintain a stack `list[tuple[int, str]]` of `(level, heading_text)`.
3. For each item:
   - If heading: compute `level`.
     - Prefer `infer_heading_level(text)` (numbered prefix is authoritative: `4.1.3.5` → 4, `A.1` → 2).
     - If not numbered, fall back to `getattr(item, "heading_level", None)` (Docling's own level). If that is None, default to 1.
     - If `_is_noisy_toc_heading(text)`, do NOT push onto stack. Still record the current stack as this item's snapshot.
     - Otherwise, pop entries with `level >= self.level`, then push.
   - Regardless of kind, record `snapshot[id(item)] = [text for _, text in stack]`.
4. Return `snapshot`.

In `build_chunk_record`, new parameter `item_lineages: dict[int, list[str]] | None = None`:

```python
def build_chunk_record(doc_id, chunk_id, chunk_index, chunk, contextualized_text,
                       item_lineages=None):
    doc_items = list(getattr(chunk.meta, "doc_items", []) or [])
    chunker_headings = list(getattr(chunk.meta, "headings", None) or [])
    lineage: list[str] = []
    if item_lineages and doc_items:
        lineage = item_lineages.get(id(doc_items[0])) or []
    # Fallback if the chunker's first item isn't in the map
    if not lineage:
        lineage = chunker_headings  # preserves current behavior
    ...
    return {
        ...
        "heading_path": lineage,
        "section_id": lineage[-1] if lineage else "root",
        ...
    }
```

`section_key_from_headings` keeps its current contract (`" / ".join(headings)` if needed elsewhere) but we stop using it for `section_id` — we take the leaf directly from the lineage. This keeps `sections.jsonl` grouping stable.

Converter (`converter.py`) wires this up:

```python
item_lineages = build_doc_item_lineages(doc)
chunk_records = build_chunk_records(doc_id, chunks, contextualize,
                                    item_lineages=item_lineages)
```

### Test cases (TDD)

In `tests/test_indexing.py`:

1. `test_build_doc_item_lineages_numbered_hierarchy` — three headings "1 A", "1.1 B", "1.1.1 C"; non-heading item after each. Each non-heading item's snapshot matches the stack up to that point. Ensures levels 1/2/3 stack correctly.
2. `test_build_doc_item_lineages_pops_on_sibling_numbered_heading` — "1 A", "1.1 B", then "2 D". After seeing "2 D", a subsequent item's snapshot is `["2 D"]`, not `["1 A", "1.1 B", "2 D"]`.
3. `test_build_doc_item_lineages_skips_noisy_heading_from_stack` — "4.1.3.1 Foo", "Note:", item under Note. Item snapshot is `["4.1.3.1 Foo"]` (Note: is not pushed but item still reads from stack).
4. `test_build_doc_item_lineages_uses_docling_heading_level_for_unnumbered` — when heading text has no numeric prefix, fall back to `item.heading_level` set by Docling.
5. `test_build_chunk_record_with_lineage_uses_full_path` — integration: a chunk whose first doc_item is under a 4-deep hierarchy gets `heading_path` of length 4 and `section_id` equal to the leaf.
6. `test_build_chunk_record_without_lineage_preserves_chunker_headings` — backward compat: if `item_lineages` is None, falls back to `chunk.meta.headings`.

### Downstream impact

- `sections.jsonl` inherits `heading_path` from chunks → sections now carry their full hierarchy too. `section_id` stays the leaf so section grouping is identical.
- `toc.json` unchanged (built directly from doc headings, not from chunks).
- `cross_refs.jsonl` unchanged (chunk_ids only, no heading_path).
- README unchanged (uses `toc.json` for the chapter outline).

---

## Polish batch (G + D + C)

### Fix G — strip standalone Cont'd lines from markdown

In `docling_bundle/converter.py`, extend `_clean_markdown_ocr_artifacts` with:

```python
_STANDALONE_CONTD_RE = re.compile(
    r"^(?:Cont(?:'d|inued)\s+on\s+next\s+page"
    r"|[-–]?\s*(?:Table\s+\d+(?:-\d+)?\s*[-–]\s*)?[Cc]ont(?:'d|inued)\s+from\s+previous\s+page)\s*$\n?",
    flags=re.MULTILINE,
)
```

Matches only standalone lines. Inline mentions in prose stay untouched (the anchored `^…$` with `re.MULTILINE` ensures start-of-line + end-of-line boundaries). Covers both directions: "on next page" and "from previous page", plus the `Table N-M - cont'd from previous page` variant seen at document.md:628.

Tests:
- `test_strips_contd_on_next_page` — free-standing line removed.
- `test_strips_table_contd_from_previous_page` — with table-prefix form.
- `test_keeps_inline_contd_mention` — "For details see Cont'd section in Appendix" inside a paragraph is not matched (not anchored at start-of-line alone — it is, but has more content after, so `$` fails).

### Fix D — blank TOC-table columns

In `docling_bundle/tables.py`, wherever the table record is assembled for `tables.index.jsonl`:

```python
record = {
    ...
    "columns": [] if record_is_toc else columns,
    "is_toc": record_is_toc,
    ...
}
```

Rationale: when `is_toc=True` the table is already a TOC fragment. Its `columns` field is populated from Docling's header-row inference, which is meaningless for TOC tables (row 1 is the first TOC row, not a header). Blanking prevents downstream consumers from mis-advertising column schema. Leaving `columns` as `[]` is preferable to omitting because the field is part of the documented schema.

Tests:
- `test_export_tables_blanks_columns_for_toc_table`
- `test_export_tables_keeps_columns_for_regular_table`

### Fix C — populate `rows` count

In the same export path, set `rows` from the Docling `TableItem.data.num_rows` attribute when available (DoclingCore exposes this on structured tables). If unavailable, count CSV data rows (`len(rows_iter)` or line count minus header).

```python
try:
    row_count = table_item.data.num_rows
except AttributeError:
    row_count = None
# later fallback: count CSV lines after writing
```

Rationale: the schema has `rows: null` on every table today. Populating it from Docling's native structured data is free information. An agent triaging a long `tables.index.jsonl` can now filter by size (e.g. "pinout tables with ≥30 rows") without reading every CSV.

Tests:
- `test_export_tables_populates_row_count_from_docling_data`
- `test_export_tables_falls_back_to_csv_line_count`

---

## Validation gate

After each commit:

1. `pytest` green (currently 167/167; add 6 new A tests + 4 new polish tests ≈ 177/177).
2. `docling/.venv/bin/python -m docling_bundle convert …` reruns cleanly.
3. Manifest counts: `chunk_count=309`, `alert_count=3`, `section_count` stable (136 after P55).
4. Integrity sweep: zero dangling `chunk_id` / `table_id` / `asset_id` references; 309/309 chunk coverage in `sections.jsonl`.
5. Spot check: a chunk at p.51 (under `4.2.1.1 UART Controller`) has `heading_path` containing `4 Functional Description`, `4.2 Peripherals`, `4.2.1 Connectivity Interface`, `4.2.1.1 UART Controller`.
6. Spot check: `document.md` has zero `Cont'd on next page` standalone lines.
7. Spot check: `tables.index.jsonl` entries for TOC tables have `columns: []`; non-TOC tables keep their columns.
8. Spot check: every `tables.index.jsonl` entry has `rows: <int>`, not null.

## Commit plan

1. **Commit 1**: Fix A — heading breadcrumbs. Includes `build_doc_item_lineages` helper, wiring through converter, 6 new tests. Updates `progress.md` + `task_plan.md` Phase 56a.
2. **Commit 2**: Polish batch G + D + C. 4 new tests. Updates `progress.md` + `task_plan.md` Phase 56b.

Rollback path: each commit stands alone; revert A without touching polish (and vice versa) if a regression surfaces.
