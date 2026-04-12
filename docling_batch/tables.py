from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


TABLE_CAPTION_RE = re.compile(r"Table\s+\d+(?:-\d+)?\.\s+\S")


@dataclass(frozen=True)
class ExportedTable:
    record: dict
    markdown: str


def build_table_manifest_records(
    doc_id: str,
    table_index: int,
    page_start: int | None,
    page_end: int | None,
    csv_path: Path,
    html_path: Path,
    label: str,
    caption: str,
) -> dict:
    return {
        "table_id": f"{doc_id}:table:{table_index:04d}",
        "page_start": page_start,
        "page_end": page_end,
        "csv_path": str(csv_path),
        "html_path": str(html_path),
        "label": label,
        "caption": caption,
    }


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
    return (
        f"Table sidecars: [HTML]({record['html_path']}) | "
        f"[CSV]({record['csv_path']}) | `{record['table_id']}`"
    )


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
                + f" [HTML]({record['html_path']}) [CSV]({record['csv_path']})"
            )
        updated = f"{updated}\n\n" + "\n".join(appendix_lines)

    return updated.rstrip() + "\n"


def export_tables(doc_id: str, tables, tables_dir: Path, doc=None) -> list[ExportedTable]:
    tables_dir.mkdir(parents=True, exist_ok=True)
    records: list[ExportedTable] = []
    for index, table in enumerate(tables, start=1):
        csv_name = Path(f"table_{index:04d}.csv")
        html_name = Path(f"table_{index:04d}.html")
        csv_path = tables_dir / csv_name
        html_path = tables_dir / html_name

        dataframe = table.export_to_dataframe(doc=doc)
        dataframe.to_csv(csv_path, index=False)
        table_html = table.export_to_html(doc=doc)
        html_path.write_text(table_html, encoding="utf-8")
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
                    html_path=Path("tables") / html_name,
                    label=_stringify_label(getattr(table, "label", None)),
                    caption=extract_table_caption(table_markdown, table_html),
                ),
                markdown=table_markdown,
            )
        )

    return records
