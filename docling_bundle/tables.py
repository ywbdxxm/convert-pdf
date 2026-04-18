from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from docling_bundle.patterns import TABLE_CAPTION_RE


# Substring groups for classify_table_kind; checked in priority order.
PINOUT_COLUMN_MARKERS = (
    "pin no",
    "pin name",
    "pin type",
    "io mux function",
    "gpio",
)
STRAP_COLUMN_MARKERS = ("strapping pin",)
REVISION_COLUMN_MARKERS = ("release notes",)
REGISTER_COLUMN_MARKERS = ("bit field", "bit range", "field name", "bits")
REGISTER_SECONDARY_MARKERS = ("reset", "attribute", "access")
ELECTRICAL_COLUMN_SET = frozenset({"parameter", "min", "typ", "max"})
TIMING_COLUMN_MARKERS = ("setup", "hold", "rise time", "fall time", "t setup", "t hold")

# Word-boundary match for the min/typ/max signal. Avoids false positives on
# prose column titles like "Minimum Value" / "Typical Time Period" / "Maximum".
_MTM_TOKEN_RE = re.compile(r"\b(min|typ|max)\b", flags=re.IGNORECASE)
# Time-unit suffix in a column header, e.g. ``(ns)``, ``(µs)``, ``(µ s)``,
# ``(us)``, ``(ms)``, ``(ps)``. When the table already looks electrical (≥2
# of min/typ/max), promoting it to ``timing`` is a tighter label for agents.
_TIME_UNIT_RE = re.compile(
    r"\(\s*(?:µ\s*s|us|ms|ns|ps)\s*\)", flags=re.IGNORECASE
)


@dataclass(frozen=True)
class ExportedTable:
    record: dict
    markdown: str


def classify_table_kind(columns: list[str]) -> str:
    """Infer a semantic kind for an engineering table from its CSV columns.

    Returns one of:
    ``pinout`` | ``strap`` | ``register`` | ``electrical`` | ``timing``
    | ``revision`` | ``generic``.
    """
    if not columns:
        return "generic"
    cols_lower = [str(c).lower() for c in columns]
    col_set = set(cols_lower)

    for marker in PINOUT_COLUMN_MARKERS:
        if any(marker in col for col in cols_lower):
            return "pinout"
    for marker in STRAP_COLUMN_MARKERS:
        if any(marker in col for col in cols_lower):
            return "strap"
    for marker in REVISION_COLUMN_MARKERS:
        if any(marker in col for col in cols_lower):
            return "revision"

    has_register_primary = any(
        any(marker in col for col in cols_lower) for marker in REGISTER_COLUMN_MARKERS
    )
    has_register_secondary = any(
        any(marker in col for col in cols_lower) for marker in REGISTER_SECONDARY_MARKERS
    )
    if has_register_primary and has_register_secondary:
        return "register"

    if ELECTRICAL_COLUMN_SET.issubset(col_set):
        return "electrical"

    # Relaxed electrical / timing fallback. Real datasheets routinely embed
    # units inside the column name (``Min (dBm)``), use ``Symbol`` instead
    # of ``Parameter``, or drop ``Typ`` on absolute-max tables — all of
    # which defeat the strict subset check above. Requiring ≥2 of
    # {min, typ, max} as whole-word hits keeps the fallback conservative:
    # a single hint (e.g. a column named "Typical Time Period") is not
    # enough to leave ``generic``.
    mtm_hits: set[str] = set()
    for col in cols_lower:
        for match in _MTM_TOKEN_RE.finditer(col):
            mtm_hits.add(match.group(1).lower())
    if len(mtm_hits) >= 2:
        if any(_TIME_UNIT_RE.search(col) for col in cols_lower):
            return "timing"
        return "electrical"

    for marker in TIMING_COLUMN_MARKERS:
        if any(marker in col for col in cols_lower):
            return "timing"

    return "generic"


def build_table_manifest_records(
    doc_id: str,
    table_index: int,
    page_start: int | None,
    page_end: int | None,
    csv_path: Path,
    label: str,
    caption: str,
    columns: list[str] | None = None,
    rows: int | None = None,
) -> dict:
    is_toc = label == "document_index"
    kind = "document_index" if is_toc else classify_table_kind(columns or [])
    # TOC tables have no meaningful column schema — their "header row" is
    # actually the first TOC entry. Blank the list so agents filtering
    # tables.index.jsonl by column names don't get misled.
    effective_columns: list[str] = [] if is_toc else list(columns) if columns else []
    record = {
        "table_id": f"{doc_id}:table:{table_index:04d}",
        "page_start": page_start,
        "page_end": page_end,
        "csv_path": str(csv_path),
        "label": label,
        "caption": caption,
        "kind": kind,
        "is_toc": is_toc,
        "rows": rows,
    }
    # Keep the ``columns`` key present when there is data to advertise; emit
    # an empty list explicitly for TOC tables so consumers see "no schema"
    # rather than "field missing"; drop for non-TOC tables without columns
    # to preserve the current contract of absence.
    if is_toc:
        record["columns"] = []
    elif effective_columns:
        record["columns"] = effective_columns
    return record


def _columns_are_similar(a: list[str], b: list[str], minimum: int = 3) -> bool:
    """Return True when two CSV column headers likely describe the same table.

    Checks that at least ``minimum`` leading columns match (case-insensitive,
    whitespace-normalised). Used to detect multi-page continuation tables.
    """
    if not a or not b:
        return False
    norm_a = [" ".join(str(c).lower().split()) for c in a]
    norm_b = [" ".join(str(c).lower().split()) for c in b]
    if norm_a == norm_b:
        return True
    compare_len = min(minimum, len(norm_a), len(norm_b))
    if compare_len < minimum:
        return False
    return norm_a[:compare_len] == norm_b[:compare_len]


def _pages_are_contiguous(prev_record: dict, current_record: dict) -> bool:
    """Adjacency check: current table starts within 1 page of previous end.

    Same page is allowed (Docling sometimes splits one logical table on one
    page into multiple records). Strictly forbids backwards jumps and any
    gap greater than one page.
    """
    prev_end = prev_record.get("page_end")
    curr_start = current_record.get("page_start")
    if prev_end is None or curr_start is None:
        return False
    return prev_end <= curr_start <= prev_end + 1


_EXPLICIT_CONTINUATION_RE = re.compile(
    r"^Table\s+(?P<target>[A-Z]?\.?\d+(?:[-.]\d+)*)\s*[-–—]\s*"
    r"cont(?:'d|inued)?(?:\s+from\s+previous\s+page)?\s*$",
    flags=re.IGNORECASE,
)

_PREV_CAPTION_NUMBER_RE = re.compile(
    r"^Table\s+(?P<target>[A-Z]?\.?\d+(?:[-.]\d+)*)",
    flags=re.IGNORECASE,
)


def _table_number(caption: str) -> str | None:
    match = _PREV_CAPTION_NUMBER_RE.match(caption or "")
    if not match:
        return None
    return match.group("target").replace(" ", "")


_CONT_SUFFIX_RE = re.compile(r"\s*\(cont'd\)\s*$", flags=re.IGNORECASE)


def _base_caption(caption: str) -> str:
    """Strip any existing ``(cont'd)`` suffix so chained continuations stay single-suffixed."""
    return _CONT_SUFFIX_RE.sub("", caption).rstrip()


def propagate_continuation_captions(exported_tables: list[ExportedTable]) -> None:
    """Normalize multi-page table captions and inherit missing ones.

    Two paths, both requiring page adjacency with the previous captioned
    engineering table:

    A. The current caption already declares continuation explicitly
       (``Table X-Y - cont'd from previous page``). When the number
       matches the previous caption, replace with ``"<prev> (cont'd)"``
       so the whole bundle uses one consistent continuation suffix.

    B. The current caption is empty AND leading column headers match the
       previous table. Inherit ``"<prev> (cont'd)"``.

    Both paths record ``continuation_of = <previous table_id>``.

    The page-adjacency requirement avoids false links between unrelated
    tables that happen to share column headers across distant pages.
    """
    previous: ExportedTable | None = None
    for exported in exported_tables:
        record = exported.record
        if record.get("label") == "document_index":
            continue

        caption = (record.get("caption") or "").strip()
        columns = record.get("columns") or []

        explicit_match = _EXPLICIT_CONTINUATION_RE.match(caption) if caption else None

        if previous is not None and _pages_are_contiguous(previous.record, record):
            prev_caption = (previous.record.get("caption") or "").strip()
            prev_columns = previous.record.get("columns") or []
            prev_number = _table_number(prev_caption)

            if explicit_match:
                current_target = explicit_match.group("target").replace(" ", "")
                if prev_number and current_target == prev_number:
                    record["caption"] = f"{_base_caption(prev_caption)} (cont'd)"
                    record["continuation_of"] = previous.record["table_id"]

            elif not caption and prev_caption and _columns_are_similar(columns, prev_columns):
                record["caption"] = f"{_base_caption(prev_caption)} (cont'd)"
                record["continuation_of"] = previous.record["table_id"]

        # Advance the "previous" cursor only when the current record has a
        # caption that could act as a donor for later tables. A continuation
        # table inherits caption but its own caption is now non-empty, so it
        # will still serve as previous for its successor (allowing chained
        # continuations like Table X-Y page 1 → page 2 → page 3).
        if (record.get("caption") or "").strip():
            previous = exported


def _stringify_label(label) -> str:
    if label is None:
        return "table"
    return getattr(label, "value", None) or str(label)


def _extract_table_caption(table_markdown: str) -> str:
    for line in table_markdown.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("|"):
            return ""
        return stripped
    return ""


def _extract_caption_from_html(html: str) -> str:
    matches = re.findall(r"<(?:th|td)[^>]*>(.*?)</(?:th|td)>", html, flags=re.IGNORECASE | re.DOTALL)
    for match in matches:
        text = re.sub(r"<[^>]+>", "", match)
        text = " ".join(text.split())
        if TABLE_CAPTION_RE.search(text):
            caption_match = TABLE_CAPTION_RE.search(text)
            if caption_match:
                return text[caption_match.start() :].strip()
    return ""


def extract_table_caption(table_markdown: str, table_html: str) -> str:
    caption = _extract_table_caption(table_markdown)
    if caption:
        return caption
    return _extract_caption_from_html(table_html)


def _format_page_span(page_start: int | None, page_end: int | None) -> str:
    if page_start is None and page_end is None:
        return "p.?"
    if page_start == page_end or page_end is None:
        return f"p.{page_start}"
    if page_start is None:
        return f"p.{page_end}"
    return f"p.{page_start}-{page_end}"


def _build_table_sidecars_line(record: dict) -> str:
    return f"Table sidecar: [CSV]({record['csv_path']}) | `{record['table_id']}`"


def _extract_context_caption(lines: list[str], sidecar_index: int) -> str:
    """Search backwards from sidecar line for a Table caption.

    Extends search range to cover more lines and also looks past
    page_break markers, images, and empty lines.
    """
    cursor = sidecar_index - 1
    max_distance = 30  # look back up to 30 lines
    changed = True
    while cursor >= 0 and changed and (sidecar_index - cursor) < max_distance:
        changed = False
        while cursor >= 0 and not lines[cursor].strip():
            cursor -= 1
            changed = True
        while cursor >= 0 and (
            lines[cursor].strip().startswith("|")
            or lines[cursor].strip() == "<!-- page_break -->"
            or lines[cursor].strip().startswith("![Image](")
            or lines[cursor].strip().startswith("Table sidecar:")
        ):
            cursor -= 1
            changed = True

    if cursor < 0:
        return ""

    raw = lines[cursor].strip()
    was_heading = raw.startswith("#")
    text = raw
    while text.startswith("#"):
        text = text[1:].strip()

    if TABLE_CAPTION_RE.match(text):
        return text
    # Heading-as-caption fallback: some datasheets title tables via a section
    # heading (e.g. "## Revision History", "## Datasheet Versioning") rather
    # than a "Table N-N." caption. Accept a narrow, universally recognizable
    # allowlist so this does not misclassify generic headings.
    if was_heading and text in _HEADING_CAPTION_ALLOWLIST:
        return text
    return ""


_HEADING_CAPTION_ALLOWLIST = frozenset({
    "Revision History",
    "Document Change Notification",
    "Datasheet Versioning",
})


def backfill_table_captions_from_markdown(markdown: str, exported_tables: list[ExportedTable]) -> None:
    if not exported_tables:
        return

    table_map = {table.record["table_id"]: table for table in exported_tables if not (table.record.get("caption") or "").strip()}
    if not table_map:
        return

    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("Table sidecar:"):
            continue
        for table_id, exported_table in table_map.items():
            if f"`{table_id}`" not in line:
                continue
            caption = _extract_context_caption(lines, index)
            if caption:
                exported_table.record["caption"] = caption
            break


def inject_table_sidecars_into_markdown(markdown: str, exported_tables: list[ExportedTable]) -> str:
    """Inject table sidecar links into markdown after each table.

    Optimized to O(m + n log n) where m = len(markdown), n = len(exported_tables).
    Previous implementation was O(n × m) due to repeated linear scans.
    """
    if not exported_tables:
        return markdown.rstrip() + "\n"

    # Build a list of all table occurrences in markdown (single O(m) scan)
    matches: list[tuple[int, int, int]] = []  # (pos, end, table_index)
    for i, exported_table in enumerate(exported_tables):
        table_markdown = exported_table.markdown.strip()
        if not table_markdown:
            continue
        # Find all occurrences of this table in markdown
        start = 0
        while True:
            pos = markdown.find(table_markdown, start)
            if pos < 0:
                break
            matches.append((pos, pos + len(table_markdown), i))
            start = pos + len(table_markdown)

    # Sort by position and deduplicate (keep first occurrence per table)
    matches.sort(key=lambda x: x[0])
    seen_indices: set[int] = set()
    unique_matches: list[tuple[int, int, int]] = []
    for match in matches:
        table_idx = match[2]
        if table_idx not in seen_indices:
            unique_matches.append(match)
            seen_indices.add(table_idx)

    # Inject sidecars
    cursor = 0
    updated_parts: list[str] = []
    for _, match_end, table_idx in unique_matches:
        exported_table = exported_tables[table_idx]
        updated_parts.append(markdown[cursor:match_end])
        updated_parts.append(f"\n\n{_build_table_sidecars_line(exported_table.record)}")
        cursor = match_end

    updated_parts.append(markdown[cursor:])
    updated = "".join(updated_parts).rstrip()

    # Append unmatched tables
    unmatched = [exported_tables[i] for i in range(len(exported_tables)) if i not in seen_indices]
    if unmatched:
        appendix_lines = ["## Table Sidecars Appendix", ""]
        for exported_table in unmatched:
            record = exported_table.record
            caption = record.get("caption") or ""
            appendix_lines.append(
                f"- {_format_page_span(record.get('page_start'), record.get('page_end'))} "
                f"`{record['table_id']}`"
                + (f" {caption}" if caption else "")
                + f" [CSV]({record['csv_path']})"
            )
        updated = f"{updated}\n\n" + "\n".join(appendix_lines)

    updated = updated.rstrip() + "\n"
    backfill_table_captions_from_markdown(updated, exported_tables)
    # Re-run continuation propagation so tables whose caption was only
    # recoverable from Markdown context can now donate to their successors.
    propagate_continuation_captions(exported_tables)
    return updated


_MIRRORED_COL_RE = re.compile(r"^(.+)\.(.+)$")


def _clean_column_header(col: str) -> str:
    """Collapse Docling's mirrored MultiIndex headers (``X.X`` → ``X``).

    When Docling's ``export_to_dataframe()`` flattens a two-level PDF header
    with identical labels on both levels (e.g. a column that spans both rows
    but only has the text in the top row), the CSV output becomes
    ``"Pin No..Pin No."``. Collapse only when the two halves match exactly
    so legitimate nested headers like ``"Pin Settings 6.At Reset"`` or data
    with dots like ``"4.1.1.3"`` are preserved.
    """
    match = _MIRRORED_COL_RE.match(col)
    if match and match.group(1).strip() == match.group(2).strip():
        return match.group(1).strip()
    return col


def export_tables(doc_id: str, tables, tables_dir: Path, doc=None) -> list[ExportedTable]:
    """Export tables to CSV + build manifest records.

    Caption-inheritance via :func:`propagate_continuation_captions` is
    intentionally NOT run here. It must run AFTER
    :func:`backfill_table_captions_from_markdown` has had a chance to recover
    captions from markdown context, otherwise the column-match heuristic
    can fill an empty caption with the previous table's title before the
    correct title (available as a markdown heading above the table) is seen.

    The full bundle pipeline calls :func:`inject_table_sidecars_into_markdown`
    which performs backfill and propagation in the correct order.
    """
    tables_dir.mkdir(parents=True, exist_ok=True)
    records: list[ExportedTable] = []
    for index, table in enumerate(tables, start=1):
        csv_name = Path(f"table_{index:04d}.csv")
        csv_path = tables_dir / csv_name

        dataframe = table.export_to_dataframe(doc=doc)
        dataframe.columns = [_clean_column_header(str(col)) for col in dataframe.columns]
        # Phase 58c: for TOC tables (``label="document_index"``) Docling's
        # DataFrame has no real header — columns are pandas's default
        # ``['0','1','2',...]`` index. Writing that as the first CSV row
        # just noise to an agent that opens the file directly. Skip the
        # header row; consumers already get "no schema" via the blanked
        # ``columns`` field in tables.index.jsonl.
        label = getattr(table, "label", None)
        label_str = getattr(label, "value", None) or str(label)
        is_toc = label_str == "document_index"
        dataframe.to_csv(csv_path, index=False, header=not is_toc)
        columns = list(dataframe.columns)
        table_html = table.export_to_html(doc=doc)
        table_markdown = table.export_to_markdown(doc=doc).strip()

        pages = [prov.page_no for prov in getattr(table, "prov", []) or [] if getattr(prov, "page_no", None) is not None]
        page_start = min(pages) if pages else None
        page_end = max(pages) if pages else None
        # Docling's ``TableItem.data.num_rows`` is the *total grid* row
        # count including every header grid row. Tables with a single
        # header row have num_rows = 1 + data_rows; tables with a
        # 2-level MultiIndex header (common in pin-map tables) have
        # num_rows = 2 + data_rows. Count distinct header grid-row
        # indices from ``table_cells`` and subtract so ``rows`` reports
        # *data rows* — what an agent counting CSV lines (minus the
        # written header) would see. Even TOC tables have a
        # ``column_header=True`` row in Docling's internal model, so
        # the same subtraction applies uniformly; the ``is_toc`` branch
        # from P58c only affects whether that header row is *written*
        # to the CSV file.
        rows = None
        docling_data = getattr(table, "data", None)
        if docling_data is not None:
            docling_rows = getattr(docling_data, "num_rows", None)
            if isinstance(docling_rows, int) and docling_rows >= 0:
                header_row_idx = {
                    c.start_row_offset_idx
                    for c in (getattr(docling_data, "table_cells", None) or [])
                    if getattr(c, "column_header", False)
                }
                rows = max(docling_rows - len(header_row_idx), 0)
        records.append(
            ExportedTable(
                record=build_table_manifest_records(
                    doc_id=doc_id,
                    table_index=index,
                    page_start=page_start,
                    page_end=page_end,
                    csv_path=Path("tables") / csv_name,
                    label=_stringify_label(getattr(table, "label", None)),
                    caption=extract_table_caption(table_markdown, table_html),
                    columns=columns,
                    rows=rows,
                ),
                markdown=table_markdown,
            )
        )

    return records
