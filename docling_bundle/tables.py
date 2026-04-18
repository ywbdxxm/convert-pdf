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
) -> dict:
    is_toc = label == "document_index"
    kind = "document_index" if is_toc else classify_table_kind(columns or [])
    record = {
        "table_id": f"{doc_id}:table:{table_index:04d}",
        "page_start": page_start,
        "page_end": page_end,
        "csv_path": str(csv_path),
        "label": label,
        "caption": caption,
        "kind": kind,
        "is_toc": is_toc,
    }
    if columns:
        record["columns"] = list(columns)
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


def propagate_continuation_captions(exported_tables: list[ExportedTable]) -> None:
    """Let captionless tables inherit caption from the previous continuation table.

    A table is treated as a continuation when:
    - it has no caption, and
    - the preceding engineering table has a caption, and
    - their leading CSV column headers match.

    On match, the current record gets ``caption`` = ``"<prev> (cont'd)"`` and
    ``continuation_of`` = the preceding ``table_id``.
    """
    previous: ExportedTable | None = None
    for exported in exported_tables:
        record = exported.record
        if record.get("label") == "document_index":
            continue
        caption = (record.get("caption") or "").strip()
        columns = record.get("columns") or []

        if not caption and previous is not None:
            prev_caption = (previous.record.get("caption") or "").strip()
            prev_columns = previous.record.get("columns") or []
            if prev_caption and _columns_are_similar(columns, prev_columns):
                record["caption"] = f"{prev_caption} (cont'd)"
                record["continuation_of"] = previous.record["table_id"]

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

    text = lines[cursor].strip()
    while text.startswith("#"):
        text = text[1:].strip()

    if TABLE_CAPTION_RE.match(text):
        return text
    return ""


def backfill_table_captions_from_markdown(markdown: str, exported_tables: list[ExportedTable]) -> None:
    if not exported_tables:
        return

    table_map = {table.record["table_id"]: table for table in exported_tables if not (table.record.get("caption") or "").strip()}
    if not table_map:
        return

    for index, line in enumerate(markdown.splitlines()):
        if not line.startswith("Table sidecars:"):
            continue
        for table_id, exported_table in table_map.items():
            if f"`{table_id}`" not in line:
                continue
            caption = _extract_context_caption(markdown.splitlines(), index)
            if caption:
                exported_table.record["caption"] = caption
            break


def inject_table_sidecars_into_markdown(markdown: str, exported_tables: list[ExportedTable]) -> str:
    if not exported_tables:
        return markdown.rstrip() + "\n"

    cursor = 0
    updated_parts: list[str] = []
    unmatched: list[ExportedTable] = []

    for exported_table in exported_tables:
        table_markdown = exported_table.markdown.strip()
        if not table_markdown:
            unmatched.append(exported_table)
            continue

        match_index = markdown.find(table_markdown, cursor)
        if match_index < 0:
            unmatched.append(exported_table)
            continue

        match_end = match_index + len(table_markdown)
        updated_parts.append(markdown[cursor:match_end])
        updated_parts.append(f"\n\n{_build_table_sidecars_line(exported_table.record)}")
        cursor = match_end

    updated_parts.append(markdown[cursor:])
    updated = "".join(updated_parts).rstrip()

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


def export_tables(doc_id: str, tables, tables_dir: Path, doc=None) -> list[ExportedTable]:
    tables_dir.mkdir(parents=True, exist_ok=True)
    records: list[ExportedTable] = []
    for index, table in enumerate(tables, start=1):
        csv_name = Path(f"table_{index:04d}.csv")
        csv_path = tables_dir / csv_name

        dataframe = table.export_to_dataframe(doc=doc)
        dataframe.to_csv(csv_path, index=False)
        columns = [str(col) for col in dataframe.columns]
        table_html = table.export_to_html(doc=doc)
        table_markdown = table.export_to_markdown(doc=doc).strip()

        pages = [prov.page_no for prov in getattr(table, "prov", []) or [] if getattr(prov, "page_no", None) is not None]
        page_start = min(pages) if pages else None
        page_end = max(pages) if pages else None
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
                ),
                markdown=table_markdown,
            )
        )

    propagate_continuation_captions(records)
    return records
