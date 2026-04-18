from __future__ import annotations

import re

from docling_bundle.patterns import HEADING_NUMBER_RE


NOISY_SECTION_IDS = {
    "Contents",
    "List of Tables",
    "List of T ables",
    "List of Figures",
    "Cont'd from previous page",
}

NOISY_TEXT_PATTERNS = [
    re.compile(r"submit documentation feedback", re.IGNORECASE),
]


def infer_heading_level(heading_text: str) -> int:
    """Infer the heading level from numbered heading text.

    Examples:
        "1 Overview"       → 1
        "2.1 Pin Layout"   → 2
        "4.1.3.5 PMU"      → 4
        "A.1 Appendix"     → 2
        "Wi-Fi"            → 1  (no number → default level 1)
    """
    text = heading_text.strip()
    match = HEADING_NUMBER_RE.match(text)
    if not match:
        return 1
    prefix = match.group("prefix")
    return prefix.count(".") + 1


def is_table_like_chunk(chunk) -> bool:
    for item in getattr(chunk.meta, "doc_items", []) or []:
        if item.__class__.__name__ == "TableItem":
            return True
        label = getattr(item, "label", None)
        if label is not None and "table" in str(label).lower():
            return True
    return False


def should_keep_chunk_record(record: dict) -> bool:
    section_id = record["section_id"]
    if section_id in NOISY_SECTION_IDS:
        return False
    text = (record.get("text") or "").strip()
    if not text:
        return False
    if text.isdigit():
        return False
    for pattern in NOISY_TEXT_PATTERNS:
        if pattern.search(text):
            return False
    return True


def section_key_from_headings(headings):
    if not headings:
        return "root"
    return " / ".join(headings)


def page_numbers_for_chunk(chunk):
    pages: list[int] = []
    for item in getattr(chunk.meta, "doc_items", []) or []:
        for prov in getattr(item, "prov", []) or []:
            page_no = getattr(prov, "page_no", None)
            if page_no is not None:
                pages.append(page_no)

    if not pages:
        return None, None

    return min(pages), max(pages)


def build_chunk_record(doc_id, chunk_id, chunk_index, chunk, contextualized_text):
    headings = list(getattr(chunk.meta, "headings", None) or [])
    page_start, page_end = page_numbers_for_chunk(chunk)
    if page_start is None:
        citation = doc_id
    elif page_start == page_end:
        citation = f"{doc_id} p.{page_start}"
    else:
        citation = f"{doc_id} p.{page_start}-{page_end}"

    return {
        "doc_id": doc_id,
        "chunk_id": chunk_id,
        "chunk_index": chunk_index,
        "section_id": section_key_from_headings(headings),
        "heading_path": headings,
        "page_start": page_start,
        "page_end": page_end,
        "text": chunk.text,
        "contextualized_text": contextualized_text,
        "doc_item_count": len(getattr(chunk.meta, "doc_items", []) or []),
        "table_like": is_table_like_chunk(chunk),
        "citation": citation,
    }


def build_section_records(doc_id, chunk_records):
    grouped = {}
    for chunk in chunk_records:
        section_id = chunk["section_id"]
        section = grouped.setdefault(
            section_id,
            {
                "doc_id": doc_id,
                "section_id": section_id,
                "heading_path": chunk["heading_path"],
                "heading_level": infer_heading_level(section_id),
                "page_start": chunk["page_start"],
                "page_end": chunk["page_end"],
                "chunk_count": 0,
                "text_preview": chunk["text"][:200],
            },
        )
        section["chunk_count"] += 1
        if chunk["page_start"] is not None:
            if section["page_start"] is None or chunk["page_start"] < section["page_start"]:
                section["page_start"] = chunk["page_start"]
        if chunk["page_end"] is not None:
            if section["page_end"] is None or chunk["page_end"] > section["page_end"]:
                section["page_end"] = chunk["page_end"]

    return sorted(
        grouped.values(),
        key=lambda item: (
            item["page_start"] if item["page_start"] is not None else 10**9,
            item["section_id"],
        ),
    )


def flag_suspicious_sections(
    section_records: list[dict],
    page_count: int | None,
    *,
    span_ratio_threshold: float = 0.30,
) -> None:
    """Mark sections whose page span is suspiciously large.

    A section covering more than ``span_ratio_threshold`` of the total
    document pages likely indicates a heading-detection error (e.g.
    "Note:" being treated as a top-level heading).
    """
    if not page_count or page_count <= 0:
        return
    for section in section_records:
        ps = section.get("page_start")
        pe = section.get("page_end")
        if ps is None or pe is None:
            continue
        span = pe - ps + 1
        if span / page_count > span_ratio_threshold:
            section["suspicious"] = True
            section["suspicious_reason"] = (
                f"spans {span}/{page_count} pages ({span / page_count:.0%})"
            )


def _overlaps(page_start_a, page_end_a, page_start_b, page_end_b):
    if None in {page_start_a, page_end_a, page_start_b, page_end_b}:
        return False
    return not (page_end_a < page_start_b or page_end_b < page_start_a)


def attach_table_references(chunk_records, section_records, table_records):
    for record in chunk_records:
        record["table_ids"] = [
            table["table_id"]
            for table in table_records
            if _overlaps(record.get("page_start"), record.get("page_end"), table.get("page_start"), table.get("page_end"))
        ]

    for record in section_records:
        record["table_ids"] = [
            table["table_id"]
            for table in table_records
            if _overlaps(record.get("page_start"), record.get("page_end"), table.get("page_start"), table.get("page_end"))
        ]


def build_chunk_records(doc_id, chunks, contextualize):
    records = []
    for index, chunk in enumerate(chunks, start=1):
        record = build_chunk_record(
            doc_id=doc_id,
            chunk_id=f"{doc_id}:{index:04d}",
            chunk_index=index,
            chunk=chunk,
            contextualized_text=contextualize(chunk),
        )
        if should_keep_chunk_record(record):
            records.append(record)
    return records


def build_toc(doc) -> list[dict]:
    """Build a hierarchical table of contents from the Docling document.

    Extracts headings with their page numbers and inferred levels.
    Returns a flat list sorted by page order — consumers can reconstruct
    the tree from heading_level.
    """
    toc: list[dict] = []
    if not hasattr(doc, "iterate_items"):
        return toc

    for item, _level in doc.iterate_items():
        label = getattr(item, "label", None)
        label_str = getattr(label, "value", None) or str(label) if label else ""
        if "heading" not in label_str.lower() and label_str != "section_header":
            continue

        text = ""
        if hasattr(item, "text"):
            text = item.text.strip()
        elif hasattr(item, "export_to_markdown"):
            text = item.export_to_markdown().strip()
        if not text:
            continue

        pages: list[int] = []
        for prov in getattr(item, "prov", []) or []:
            page_no = getattr(prov, "page_no", None)
            if page_no is not None:
                pages.append(page_no)

        page = min(pages) if pages else None
        level = infer_heading_level(text)

        toc.append({
            "heading": text,
            "level": level,
            "page": page,
        })

    return toc


def build_pages_index(
    chunk_records: list[dict],
    table_records: list[dict],
    alerts: list[dict],
) -> list[dict]:
    """Build a page→content reverse index.

    For each page that appears in any record, collect the chunk_ids,
    table_ids, and alert kinds present on that page.
    """
    page_data: dict[int, dict] = {}

    def _ensure_page(page: int) -> dict:
        if page not in page_data:
            page_data[page] = {
                "page": page,
                "chunk_ids": [],
                "table_ids": [],
                "alert_kinds": [],
            }
        return page_data[page]

    for chunk in chunk_records:
        ps = chunk.get("page_start")
        pe = chunk.get("page_end")
        if ps is None:
            continue
        pe = pe or ps
        for p in range(ps, pe + 1):
            entry = _ensure_page(p)
            entry["chunk_ids"].append(chunk["chunk_id"])

    for table in table_records:
        ps = table.get("page_start")
        pe = table.get("page_end")
        if ps is None:
            continue
        pe = pe or ps
        for p in range(ps, pe + 1):
            entry = _ensure_page(p)
            entry["table_ids"].append(table["table_id"])

    for alert in alerts:
        page = alert.get("page") or alert.get("page_start")
        if page is None:
            continue
        entry = _ensure_page(page)
        kind = alert.get("kind", "unknown")
        if kind not in entry["alert_kinds"]:
            entry["alert_kinds"].append(kind)

    return sorted(page_data.values(), key=lambda x: x["page"])
