from __future__ import annotations

from pathlib import Path


PAGE_BREAK = "<!-- page_break -->"


def split_markdown_pages(markdown: str) -> dict[int, str]:
    parts = markdown.split(PAGE_BREAK)
    pages: dict[int, str] = {}
    for page_no, part in enumerate(parts, start=1):
        text = part.strip()
        if not text:
            continue
        pages[page_no] = text + "\n"
    return pages


def write_page_slices(markdown: str, pages_dir: Path, doc_id: str) -> None:
    pages_dir.mkdir(parents=True, exist_ok=True)
    for page_no, content in split_markdown_pages(markdown).items():
        page_path = pages_dir / f"page_{page_no:04d}.md"
        page_path.write_text(f"# {doc_id} page {page_no}\n\n{content}", encoding="utf-8")


def build_quality_summary(
    doc_id: str,
    source_pdf_path: str,
    page_count: int | None,
    table_count: int,
    alert_count: int,
    alerts: list[dict],
) -> str:
    lines = [
        "# Quality Summary",
        "",
        f"- Doc ID: `{doc_id}`",
        f"- Source PDF: `{source_pdf_path}`",
        f"- Page count: `{page_count}`",
        f"- Table count: `{table_count}`",
        f"- Alert count: `{alert_count}`",
        "",
        "Open `README.generated.md` first, then use `sections.jsonl`, `chunks.jsonl`, `tables.index.jsonl`, or `pages/` for targeted inspection.",
    ]
    if alerts:
        lines.extend(["", "## Alerts", ""])
        for alert in alerts:
            lines.append(f"- {alert.get('kind', 'unknown')}")
    return "\n".join(lines).rstrip() + "\n"


def build_readme(
    doc_id: str,
    source_pdf_path: str,
    document_json: str,
    document_markdown: str,
    document_html: str,
    sections_index: str,
    chunks_index: str,
    tables_index: str,
    alerts_path: str,
) -> str:
    lines = [
        f"# {doc_id}",
        "",
        "## Start Here",
        "",
        "1. Read `quality-summary.md`.",
        "2. Read `document.md` for broad reading context.",
        "3. Use `sections.jsonl` for topic navigation.",
        "4. Use `chunks.jsonl` for page-aware retrieval.",
        "5. Use `tables.index.jsonl` and `tables/` for structured table verification.",
        "6. Use `pages/` when you already know the page number.",
        "7. Return to the original PDF for final engineering verification.",
        "",
        "## Key Paths",
        "",
        f"- Source PDF: `{source_pdf_path}`",
        f"- JSON: `{document_json}`",
        f"- Markdown: `{document_markdown}`",
        f"- HTML: `{document_html}`",
        f"- Sections index: `{sections_index}`",
        f"- Chunks index: `{chunks_index}`",
        f"- Tables index: `{tables_index}`",
        f"- Alerts: `{alerts_path}`",
    ]
    return "\n".join(lines).rstrip() + "\n"
