"""Extract Section / Table / Figure cross-references from document Markdown.

Chip manuals are dense with "See Section 4.1.3.5" / "Refer to Table 2-5"
/ "See Figure 3-1" style references. Flattening these into a queryable
jsonl makes navigation O(index lookup) instead of O(full-text scan).

The extractor:
- tracks current source page via ``<!-- page_break -->`` markers that
  ``converter.py`` emits during Markdown export
- matches prefix-anchored references (``see`` / ``refer to`` /
  ``shown in``) to avoid false positives from table captions
- resolves target page against ``toc`` (for Section), ``tables.index.jsonl``
  (for Table), and :func:`build_figure_page_map` (for Figure) when possible
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

# Prefix-anchored ``^Figure <id>`` match. Docling emits figure titles
# as standalone text items with ``label="caption"``; the text form is
# typically ``Figure 2-2. ESP32-S3 Power Scheme``. Prefix-anchoring
# avoids picking up running prose that happens to mention the phrase.
_FIGURE_CAPTION_TARGET_RE = re.compile(
    r"^(Figure\s+[A-Z]?\.?\d+(?:[-.]\d+)*)", flags=re.IGNORECASE
)


def build_figure_page_map(doc) -> dict[str, int]:
    """Return ``{"Figure X-Y": page_no}`` from Docling's native captions.

    Walks ``doc.texts`` and collects entries whose ``label == "caption"``
    and whose text matches ``^Figure <id>``. Uses Docling's own
    structural label — no heuristic substring matching against running
    prose — so every PDF Docling processes contributes its ground-truth
    figure locations without per-vendor tuning.

    Figures without a ``prov[0].page_no`` (Docling cache stubs, rare
    malformed items) are skipped silently; they stay unresolved in
    ``cross_refs.jsonl`` rather than pointing at a wrong page.

    First occurrence wins for duplicate ids — picking the later one
    could swap to a trailing ``(cont'd)`` caption on a later page.
    """
    texts = getattr(doc, "texts", None) or []
    figure_map: dict[str, int] = {}
    for item in texts:
        label = getattr(item, "label", None)
        label_str = getattr(label, "value", None) or str(label)
        if label_str != "caption":
            continue
        text = getattr(item, "text", "") or ""
        match = _FIGURE_CAPTION_TARGET_RE.match(text.strip())
        if not match:
            continue
        figure_id = match.group(1)
        # Normalize internal whitespace so "Figure  2-2" and "Figure 2-2"
        # collapse to the same key (matches the form used by the
        # reference regex after its own whitespace normalization).
        figure_id = re.sub(r"\s+", " ", figure_id)
        if figure_id in figure_map:
            continue
        prov = getattr(item, "prov", None) or []
        if not prov:
            continue
        page_no = getattr(prov[0], "page_no", None)
        if page_no is None:
            continue
        figure_map[figure_id] = page_no
    return figure_map


def _resolve_figure_page(target: str, figure_page_map: dict[str, int]) -> int | None:
    if not target or not figure_page_map:
        return None
    key = f"Figure {target.strip()}"
    return figure_page_map.get(key)


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
    chunk_records: list[dict] | None = None,
    figure_page_map: dict[str, int] | None = None,
) -> list[dict]:
    """Return a flat list of cross-references with optional target-page resolution.

    Each record has fields:
    - ``kind``: "section" | "table" | "figure"
    - ``target``: the numeric/alphanumeric anchor (e.g. "4.1.3.5", "2-5")
    - ``source_page``: page on which the reference appears (1-indexed)
    - ``source_chunk_id``: chunk containing the reference (best-effort match)
    - ``target_page``: resolved page, or ``None``
    - ``unresolved``: ``True`` when ``target_page`` could not be resolved
    - ``raw``: the matched text

    ``source_chunk_id`` is populated via best-effort matching: the reference's
    ``raw`` text is searched in chunks on the same ``source_page``. When no
    match is found, the field is omitted (not set to ``None``).
    """
    toc = toc or []
    table_records = table_records or []
    chunk_records = chunk_records or []
    figure_page_map = figure_page_map or {}

    refs: list[dict] = []
    current_page = 1

    for raw_line in markdown.splitlines():
        if raw_line.strip() == PAGE_BREAK_MARKER:
            current_page += 1
            continue
        for match in CROSS_REF_RE.finditer(raw_line):
            kind = _normalize_kind(match.group("kind"))
            target = match.group("target").strip()
            raw_text = match.group(0)
            record: dict = {
                "kind": kind,
                "target": target,
                "source_page": current_page,
                "raw": raw_text,
            }
            if kind == "section":
                target_page = _resolve_section_page(target, toc)
            elif kind == "table":
                target_page = _resolve_table_page(target, table_records)
            elif kind == "figure":
                target_page = _resolve_figure_page(target, figure_page_map)
            else:
                target_page = None
            record["target_page"] = target_page
            if target_page is None:
                record["unresolved"] = True

            # Best-effort source_chunk_id: find chunk on same page containing raw text
            source_chunk_id = _find_source_chunk(current_page, raw_text, chunk_records)
            if source_chunk_id:
                record["source_chunk_id"] = source_chunk_id

            refs.append(record)

    return refs


def _find_source_chunk(page: int, raw_text: str, chunk_records: list[dict]) -> str | None:
    """Return chunk_id of the first chunk on ``page`` containing ``raw_text``.

    Case-insensitive substring match against chunk ``text`` field. Returns
    ``None`` when no match is found (caller omits the field).
    """
    needle = raw_text.lower()
    for chunk in chunk_records:
        ps = chunk.get("page_start")
        pe = chunk.get("page_end")
        if ps is None or pe is None:
            continue
        if not (ps <= page <= pe):
            continue
        haystack = (chunk.get("text") or "").lower()
        if needle in haystack:
            return chunk["chunk_id"]
    return None
