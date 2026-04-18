"""Extract Section / Table / Figure cross-references from document Markdown.

Chip manuals are dense with "See Section 4.1.3.5" / "Refer to Table 2-5"
/ "See Figure 3-1" style references. Flattening these into a queryable
jsonl makes navigation O(index lookup) instead of O(full-text scan).

The extractor:
- tracks current source page via ``<!-- page_break -->`` markers that
  ``converter.py`` emits during Markdown export
- matches prefix-anchored references (``see`` / ``refer to`` /
  ``shown in``) to avoid false positives from table captions
- resolves target page against ``toc`` (for Section) and
  ``tables.index.jsonl`` (for Table) when possible
- leaves Figure targets unresolved until a figure index exists
"""

from __future__ import annotations

import re


# The reference prefix anchors the match so plain "Table 2-5." appearing
# inside a caption is NOT mistaken for a reference.
_PREFIX = r"(?:\bsee\b|\brefer\s+to\b|\bshown\s+in\b|\bas\s+shown\s+in\b)"

# "Table" is sometimes broken into "T able" by Docling's OCR on certain
# header fonts; accept both.
_KIND_RAW = r"(?:Section|Figure|Table|T\s+able)"

# Numbered targets: 4, 4.1, 4.1.3.5, A.1, 2-5, 3-1, etc.
_TARGET_RAW = r"[A-Z]?\.?\d+(?:[-.]\d+)*"

CROSS_REF_RE = re.compile(
    rf"{_PREFIX}\s+(?P<kind>{_KIND_RAW})\s+(?P<target>{_TARGET_RAW})",
    flags=re.IGNORECASE,
)

PAGE_BREAK_MARKER = "<!-- page_break -->"


def _normalize_kind(kind_text: str) -> str:
    normalized = re.sub(r"\s+", "", kind_text).lower()
    if normalized == "table":
        return "table"
    if normalized == "section":
        return "section"
    if normalized == "figure":
        return "figure"
    return normalized


def _resolve_section_page(target: str, toc: list[dict]) -> int | None:
    if not target:
        return None
    needle = f"{target} "
    for entry in toc:
        heading = entry.get("heading") or ""
        if heading == target or heading.startswith(needle):
            return entry.get("page")
    return None


_TABLE_CAPTION_TARGET_RE = re.compile(
    r"^Table\s+([A-Z]?\.?\d+(?:[-.]\d+)*)", flags=re.IGNORECASE
)


def _resolve_table_page(target: str, table_records: list[dict]) -> int | None:
    if not target:
        return None
    normalized_target = target.replace(" ", "")
    for record in table_records:
        caption = record.get("caption") or ""
        match = _TABLE_CAPTION_TARGET_RE.match(caption)
        if not match:
            continue
        caption_target = match.group(1).replace(" ", "")
        if caption_target == normalized_target:
            return record.get("page_start")
    return None


def extract_cross_refs(
    markdown: str,
    toc: list[dict] | None = None,
    table_records: list[dict] | None = None,
) -> list[dict]:
    """Return a flat list of cross-references with optional target-page resolution.

    Each record has fields:
    - ``kind``: "section" | "table" | "figure"
    - ``target``: the numeric/alphanumeric anchor (e.g. "4.1.3.5", "2-5")
    - ``source_page``: page on which the reference appears (1-indexed)
    - ``target_page``: resolved page, or ``None``
    - ``unresolved``: ``True`` when ``target_page`` could not be resolved
    - ``raw``: the matched text
    """
    toc = toc or []
    table_records = table_records or []

    refs: list[dict] = []
    current_page = 1

    for raw_line in markdown.splitlines():
        if raw_line.strip() == PAGE_BREAK_MARKER:
            current_page += 1
            continue
        for match in CROSS_REF_RE.finditer(raw_line):
            kind = _normalize_kind(match.group("kind"))
            target = match.group("target").strip()
            record: dict = {
                "kind": kind,
                "target": target,
                "source_page": current_page,
                "raw": match.group(0),
            }
            if kind == "section":
                target_page = _resolve_section_page(target, toc)
            elif kind == "table":
                target_page = _resolve_table_page(target, table_records)
            else:
                target_page = None
            record["target_page"] = target_page
            if target_page is None:
                record["unresolved"] = True
            refs.append(record)

    return refs
