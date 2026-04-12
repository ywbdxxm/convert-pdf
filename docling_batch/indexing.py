from __future__ import annotations

import re


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
                "heading_level": len(chunk["heading_path"]),
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
