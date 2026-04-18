from __future__ import annotations

from collections import Counter


# Cap chapter outline length so very large TRMs don't bloat the README.
# A chapter-heavy manual can still be explored through toc.json; the
# outline only needs to give agents an initial orientation.
_MAX_CHAPTERS_IN_README = 40


def _format_page_span(alert: dict) -> str:
    page_start = alert.get("page_start", alert.get("page"))
    page_end = alert.get("page_end", alert.get("page"))
    if page_start is None and page_end is None:
        return ""
    if page_start == page_end or page_end is None:
        return f" p.{page_start}"
    if page_start is None:
        return f" p.{page_end}"
    return f" p.{page_start}-{page_end}"


def _format_alert_line(alert: dict) -> str:
    kind = alert.get("kind", "unknown")
    span = _format_page_span(alert)
    detail = alert.get("caption") or alert.get("detail") or ""
    line = f"- {kind}{span}"
    if detail:
        line += f": {detail}"
    # Surface the fallback image when the alert carries one so the agent
    # can jump straight to the replacement visual evidence.
    image_path = alert.get("image_path")
    if image_path:
        line += f" → fallback image `{image_path}`"
    return line


def _chapter_outline_lines(toc: list[dict]) -> list[str]:
    chapters = [entry for entry in toc if entry.get("is_chapter")]
    if not chapters:
        return []
    lines = ["", "## Chapter Outline", ""]
    for entry in chapters[:_MAX_CHAPTERS_IN_README]:
        page = entry.get("page")
        heading = entry.get("heading", "")
        page_prefix = f"p.{page}: " if page is not None else ""
        lines.append(f"- {page_prefix}{heading}")
    if len(chapters) > _MAX_CHAPTERS_IN_README:
        lines.append(f"- … ({len(chapters) - _MAX_CHAPTERS_IN_README} more — see `toc.json`)")
    return lines


def _table_breakdown_lines(table_records: list[dict]) -> list[str]:
    if not table_records:
        return []
    kind_counter = Counter(record.get("kind", "generic") for record in table_records)
    # Skip document_index from the user-visible summary — it is filtered
    # through the `is_toc` flag.
    kind_counter.pop("document_index", None)
    if not kind_counter:
        return []
    lines = ["", "## Table Breakdown", ""]
    for kind in ("pinout", "register", "electrical", "timing", "strap", "revision", "generic"):
        count = kind_counter.get(kind, 0)
        if count:
            lines.append(f"- {kind}: `{count}`")
    # Surface any unexpected kinds that may have been added later.
    for kind, count in kind_counter.items():
        if kind not in {"pinout", "register", "electrical", "timing", "strap", "revision", "generic"}:
            lines.append(f"- {kind}: `{count}`")
    return lines


def _cross_refs_summary_lines(cross_refs: list[dict]) -> list[str]:
    if not cross_refs:
        return []
    kind_counter = Counter(record.get("kind", "unknown") for record in cross_refs)
    resolved = sum(1 for record in cross_refs if not record.get("unresolved"))
    total = len(cross_refs)
    rate = f"{100 * resolved // total}%" if total else "0%"
    lines = ["", "## Cross-Reference Summary", ""]
    lines.append(f"- Total: `{total}` (resolved: `{resolved}` / {rate})")
    for kind in ("section", "table", "figure"):
        count = kind_counter.get(kind, 0)
        if count:
            lines.append(f"- {kind}: `{count}`")
    return lines


def build_readme(
    doc_id: str,
    source_pdf_path: str,
    page_count: int | None,
    table_count: int,
    alert_count: int,
    alerts: list[dict],
    document_json: str,
    document_markdown: str,
    document_html: str,
    sections_index: str,
    chunks_index: str,
    tables_index: str,
    alerts_path: str,
    toc: list[dict] | None = None,
    table_records: list[dict] | None = None,
    cross_refs: list[dict] | None = None,
    toc_path: str = "toc.json",
    pages_index_path: str = "pages.index.jsonl",
    cross_refs_path: str = "cross_refs.jsonl",
    assets_index_path: str = "assets.index.jsonl",
) -> str:
    lines = [
        f"# {doc_id}",
        "",
        "## Summary",
        "",
        f"- Source PDF: `{source_pdf_path}`",
        f"- Page count: `{page_count}`",
        f"- Table count: `{table_count}`",
        f"- Alert count: `{alert_count}`",
        "",
        "## Start Here",
        "",
        "1. Read `document.md` for broad reading context.",
        "2. Use `toc.json` (filter `is_chapter=true`) for the chapter outline.",
        "3. Use `pages.index.jsonl` to look up all content on a given page.",
        "4. Use `sections.jsonl` for fine-grained section navigation.",
        "5. Use `tables.index.jsonl` (filter `kind`) for pinout/register/electrical table lookup.",
        "6. Use `cross_refs.jsonl` to jump between referenced sections, tables, and figures.",
        "7. Use `assets.index.jsonl` to find images on any page.",
        "8. Return to the original PDF for final engineering verification.",
        "",
        "## Key Files",
        "",
        f"- JSON: `{document_json}`",
        f"- Markdown: `{document_markdown}`",
        f"- HTML: `{document_html}`",
        f"- Table of Contents: `{toc_path}`",
        f"- Pages index: `{pages_index_path}`",
        f"- Sections index: `{sections_index}`",
        f"- Chunks index: `{chunks_index}`",
        f"- Tables index: `{tables_index}`",
        f"- Cross-references: `{cross_refs_path}`",
        f"- Assets index: `{assets_index_path}`",
        f"- Alerts: `{alerts_path}`",
    ]

    lines.extend(_chapter_outline_lines(toc or []))
    lines.extend(_table_breakdown_lines(table_records or []))
    lines.extend(_cross_refs_summary_lines(cross_refs or []))

    if alerts:
        lines.extend(["", "## Alerts", ""])
        for alert in alerts:
            lines.append(_format_alert_line(alert))

    return "\n".join(lines).rstrip() + "\n"
