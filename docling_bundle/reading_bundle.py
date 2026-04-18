from __future__ import annotations

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
        "7. Return to the original PDF for final engineering verification.",
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
    if alerts:
        lines.extend(["", "## Alerts", ""])
        for alert in alerts:
            suffix = ""
            page_start = alert.get("page_start", alert.get("page"))
            page_end = alert.get("page_end", alert.get("page"))
            if page_start is not None and page_end is not None:
                suffix = f" p.{page_start}" if page_start == page_end else f" p.{page_start}-{page_end}"
            elif page_start is not None:
                suffix = f" p.{page_start}"
            detail = alert.get("caption") or alert.get("detail") or ""
            lines.append(f"- {alert.get('kind', 'unknown')}{suffix}" + (f": {detail}" if detail else ""))
    return "\n".join(lines).rstrip() + "\n"
