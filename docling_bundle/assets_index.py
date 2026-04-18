"""Build assets.index.jsonl from a bundle's Markdown.

Every PDF that Docling processes emits hash-named image files under
``assets/``. For agent lookup we want a page-keyed index:

- ``jq 'select(.page == N)' assets.index.jsonl`` → all images on page N
- ``jq 'select(.size_bytes > 50000)' assets.index.jsonl`` → substantial
  figures, filtering out tiny icons

Rather than guessing a caption for each image (high false-attribution
risk when captions span multi-image figures), the index stores only
facts we can observe directly: the hash path Docling emitted, the
source page from ``<!-- page_break -->`` markers, the markdown line the
reference lives on, and the file size. Consumers can open the file or
read the nearby Markdown context when they need more.
"""

from __future__ import annotations

from pathlib import Path

from docling_bundle.patterns import IMAGE_REF_RE


PAGE_BREAK_MARKER = "<!-- page_break -->"


def build_assets_index(doc_id: str, markdown: str, doc_dir: Path) -> list[dict]:
    """Walk the Markdown and emit one record per image reference.

    Preserves reference order (which is also document reading order).
    Missing files are flagged with ``missing: true`` so broken bundles
    surface immediately rather than pretending to be fine.
    """
    records: list[dict] = []
    current_page = 1
    seq = 0

    for line_number, raw_line in enumerate(markdown.splitlines(), start=1):
        stripped = raw_line.strip()
        if stripped == PAGE_BREAK_MARKER:
            current_page += 1
            continue

        match = IMAGE_REF_RE.search(raw_line)
        if not match:
            continue

        seq += 1
        rel_path = match.group(1)
        abs_path = doc_dir / rel_path

        record: dict = {
            "asset_id": f"{doc_id}:asset:{seq:04d}",
            "path": rel_path,
            "page": current_page,
            "md_line": line_number,
        }

        if abs_path.exists():
            try:
                record["size_bytes"] = abs_path.stat().st_size
            except OSError:
                record["missing"] = True
        else:
            record["missing"] = True

        records.append(record)

    return records
