from __future__ import annotations

import re
from collections import Counter

from docling_bundle.patterns import (
    HEADING_NUMBER_RE,
    TABLE_CAPTION_RE,
    clean_ocr_text,
    normalize_heading_text,
)


# Section-id labels whose chunk content is a literal TOC dump — every
# list_item under them is a caption + page number echoing the real TOC.
# Dropping these chunks is safe; their contents are redundant with
# ``toc.json`` and ``tables.index.jsonl``.
TOC_DROP_SECTION_IDS = {
    "Contents",
    "List of Tables",
    "List of T ables",
    "List of Figures",
}

# Section-id labels that mark a CONTINUATION context on a continued
# table page. The list_items that follow them are legitimate table
# footnotes / pin legends / cross-references — we must NOT drop their
# chunks. They are still excluded from TOC / sections / lineage layers
# (they have no meaning as navigation anchors); lineage promotion
# (:func:`build_doc_item_lineages`) reparents their chunks to the real
# numbered ancestor so ``heading_path`` / ``section_id`` are sane.
CONTINUATION_MARKER_SECTION_IDS = {
    "Cont'd from previous page",
}

# Backwards-compatible union: existing call sites treat this as the
# "noisy labels at all layers" set. Keep it as the union so TOC,
# sections, lineage, and ``should_keep_chunk_record`` all behave
# unchanged. Only :func:`build_chunk_records` narrows to the drop
# subset (:data:`TOC_DROP_SECTION_IDS`).
NOISY_SECTION_IDS = TOC_DROP_SECTION_IDS | CONTINUATION_MARKER_SECTION_IDS

NOISY_TEXT_PATTERNS = [
    re.compile(r"submit documentation feedback", re.IGNORECASE),
]

# Headings that only make sense inside a parent section context
# ("Note:" standalone, "Features" as a sub-header, "Feature List", etc.).
# When these repeat across a document they cannot anchor TOC navigation.
NOISY_TOC_HEADINGS = {
    "Note:",
    "Notes:",
    "Note",
    "Notes",
}

# A heading occurring more times than this in the document with no numbered
# prefix is treated as a section-internal label, not a navigation anchor.
# Threshold 3 keeps occasional 2x repetitions (e.g. a doc genuinely has the
# same short non-numbered heading twice) and still removes the high-volume
# structural noise ("Feature List", "Pin Assignment", "Note:" that repeat
# many times in chip manuals).
TOC_REPEAT_DROP_THRESHOLD = 3

# A heading starting with one of these Unicode bullet glyphs is a list item
# that Docling's layout analyzer mis-promoted to a section heading. Real
# chapter/section anchors never begin with a typographic bullet. We limit
# the set to Unicode bullet glyphs only — ASCII ``-`` / ``*`` / ``+`` are
# common inside legitimate titles ("Wi-Fi", "Low-Power Modes", "2.4 GHz")
# and must not be filtered.
_BULLET_HEADING_PREFIX_RE = re.compile(r"^[·•◦▪▫►◆∙⬧]")


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


def build_chunk_record(
    doc_id,
    chunk_id,
    chunk_index,
    chunk,
    contextualized_text,
    item_lineages: dict[int, list[str]] | None = None,
):
    """Build one ``chunks.jsonl`` record.

    When ``item_lineages`` is provided (see :func:`build_doc_item_lineages`),
    the chunk's ``heading_path`` is replaced with the full ancestor chain of
    its first ``doc_item``. ``section_id`` stays the leaf heading so
    ``sections.jsonl`` grouping is unchanged. Without lineage data we fall
    back to whatever depth the chunker provided via ``chunk.meta.headings``.
    """
    doc_items = list(getattr(chunk.meta, "doc_items", []) or [])
    chunker_headings = list(getattr(chunk.meta, "headings", None) or [])

    lineage: list[str] = []
    if item_lineages and doc_items:
        first_item = doc_items[0]
        lineage = list(item_lineages.get(_item_key(first_item)) or [])
    if not lineage:
        lineage = chunker_headings

    # Phase 57b: ensure heading_path / section_id use normalized display
    # text. Lineage built via build_doc_item_lineages is already normalized;
    # the chunker_headings fallback path is not, so normalize here as a
    # safety net. Normalization is idempotent.
    lineage = [normalize_heading_text(entry) for entry in lineage]

    page_start, page_end = page_numbers_for_chunk(chunk)
    if page_start is None:
        citation = doc_id
    elif page_start == page_end:
        citation = f"{doc_id} p.{page_start}"
    else:
        citation = f"{doc_id} p.{page_start}-{page_end}"

    section_id = lineage[-1] if lineage else "root"

    return {
        "doc_id": doc_id,
        "chunk_id": chunk_id,
        "chunk_index": chunk_index,
        "section_id": section_id,
        "heading_path": lineage,
        "page_start": page_start,
        "page_end": page_end,
        # Phase 57a: reverse Docling's "T able" OCR split in chunk text so
        # downstream consumers (cross_refs source-chunk matching, full-text
        # search) see the same normalized form as document.md.
        "text": clean_ocr_text(chunk.text),
        "contextualized_text": clean_ocr_text(contextualized_text),
        "doc_item_count": len(doc_items),
        "table_like": is_table_like_chunk(chunk),
        "citation": citation,
    }


def build_section_records(
    doc_id,
    chunk_records,
    *,
    dropped_repeat_labels: set[str] | None = None,
):
    """Aggregate chunks into section records, skipping noisy local labels.

    ``NOISY_TOC_HEADINGS`` (``Note:`` / ``Notes:`` / etc.) and
    ``dropped_repeat_labels`` (``Feature List`` / ``Pin Assignment`` style
    repeated sub-labels — see :func:`compute_dropped_repeat_labels`) are
    section-internal labels the chunker exposes as standalone headings.
    Both get the same treatment here:

    1. **No dedicated section record** — the TOC already hides them as
       navigation anchors, so sections.jsonl stays consistent.
    2. **Orphan chunks re-parent to the most recent kept section** —
       preserves content reachability via section-tree traversal
       (an agent looking at ``4.2.1.1 UART Controller.chunk_ids`` still
       sees its Feature List bullets).
    3. **Orphans do NOT expand the host section's page range** — the
       section's ``page_start`` / ``page_end`` reflect its numbered
       heading's authoritative scope, not the scattered sub-label
       occurrences. This is what stops reparenting from silently bringing
       ghost-span back.

    An orphan appearing before any real section is skipped (no phantom
    parent is fabricated). Document order is taken from the input
    iteration order of ``chunk_records``.
    """
    dropped = dropped_repeat_labels or set()
    grouped: dict = {}
    last_kept_section_id: str | None = None

    for chunk in chunk_records:
        section_id = chunk["section_id"]
        # An orphan chunk is one whose section_id matches any noise filter the
        # TOC applies: ``NOISY_SECTION_IDS`` / ``NOISY_TOC_HEADINGS`` / table
        # captions promoted to headings / noisy-text patterns — plus the
        # repeat-label drop set. Keeping the two layers on the same filter
        # prevents silent drift (Phase 53: Feature List; Phase 54: Table X-Y
        # captions leaking as sections when rendered as images).
        is_orphan = _is_noisy_toc_heading(section_id) or section_id in dropped

        if is_orphan:
            if last_kept_section_id is None:
                # No preceding real section to attach to yet — skip silently
                # rather than fabricate a parent from the noise heading itself.
                continue
            host = grouped[last_kept_section_id]
            host["chunk_count"] += 1
            host["chunk_ids"].append(chunk["chunk_id"])
            # Deliberately do NOT update host's page range from orphan chunks;
            # the section's scope must stay anchored to its own numbered heading.
            continue

        last_kept_section_id = section_id
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
                "chunk_ids": [],
                "text_preview": chunk["text"][:200],
            },
        )
        section["chunk_count"] += 1
        section["chunk_ids"].append(chunk["chunk_id"])
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


def build_chunk_records(
    doc_id,
    chunks,
    contextualize,
    *,
    item_lineages: dict | None = None,
):
    records = []
    for index, chunk in enumerate(chunks, start=1):
        chunker_headings = list(getattr(chunk.meta, "headings", None) or [])
        # Reject chunks whose chunker-attributed leaf is a TOC-region
        # section (Contents / List of Tables / List of T ables /
        # List of Figures). Their contents are literal TOC dumps (see
        # :data:`TOC_DROP_SECTION_IDS` docstring) that duplicate
        # ``toc.json`` / ``tables.index.jsonl``. Lineage promotion
        # (Phase 56) made ``section_id`` inherit from the chain's leaf,
        # which could resurrect TOC content — filter on the chunker's
        # view so that keep/reject semantics are unchanged.
        #
        # Phase 58a: narrowed from ``NOISY_SECTION_IDS`` to
        # :data:`TOC_DROP_SECTION_IDS`. ``Cont'd from previous page``
        # lived in the old union but marks a continuation context, not
        # a TOC dump — the list_items beneath it on continued table
        # pages are legitimate table footnotes / pin legend entries
        # that lineage promotion correctly reparents to the real
        # numbered ancestor. Dropping them erased 28 chunks on the
        # ESP32-S3 datasheet (p.16-25 pin footnotes / power legends).
        if chunker_headings and chunker_headings[-1] in TOC_DROP_SECTION_IDS:
            continue
        record = build_chunk_record(
            doc_id=doc_id,
            chunk_id=f"{doc_id}:{index:04d}",
            chunk_index=index,
            chunk=chunk,
            contextualized_text=contextualize(chunk),
            item_lineages=item_lineages,
        )
        if should_keep_chunk_record(record):
            records.append(record)
    return records


def _item_key(item) -> object:
    """Return a stable lookup key for a DoclingDocument item.

    Prefer ``self_ref`` (a JSON-pointer string like ``#/texts/42`` that
    DoclingDocument assigns to every DocItem and that ``HybridChunker``
    preserves across its own item copies). Fall back to Python object
    identity for items that don't have a ``self_ref``.
    """
    ref = getattr(item, "self_ref", None)
    if isinstance(ref, str) and ref:
        return ref
    return id(item)


def build_doc_item_lineages(
    doc,
    *,
    dropped_repeat_labels: set[str] | None = None,
) -> dict:
    """Walk the document in reading order and snapshot the heading ancestor
    chain at every item's position.

    The returned dict maps the item's stable key (:func:`_item_key` —
    ``self_ref`` when available, else ``id()``) to the list of ancestor
    headings (``[chapter, section, subsection, …]``). Using ``self_ref``
    matters because ``HybridChunker`` may re-wrap DocItems into new Python
    objects while preserving their document reference; an ``id()``-only key
    would miss those.

    Level inference:
      * Numbered headings (``4.1.3.5 …``) take precedence — the prefix is
        the authoritative level.
      * Non-numbered headings fall back to Docling's own ``heading_level``
        attribute when present, else default to 1.

    Noise handling (a heading is excluded from the stack — but its own
    snapshot still reflects the current stack, so chunks associated with
    the noisy item still inherit a sane breadcrumb):
      * ``_is_noisy_toc_heading`` — Note:, bullet-led, table captions, …
      * ``dropped_repeat_labels`` — recurring section-internal labels
        (Feature List / Pin Assignment style). Without this filter a
        30x-repeating "Feature List" would push as level 1 and clobber
        the real chapter ancestor on the stack.
    """
    snapshots: dict = {}
    if not hasattr(doc, "iterate_items"):
        return snapshots

    dropped = dropped_repeat_labels or set()
    # Each stack entry is (level, text, is_numbered). ``is_numbered`` matters
    # because a non-numbered heading mid-chapter (e.g. a bold bullet-style
    # "BACKUP32K_CLK" inside "4.1.3.9 XTAL32K Watchdog Timers") must NOT
    # pop out the numbered chapter ancestors — the numbered structure is
    # authoritative. Non-numbered headings become children of the deepest
    # numbered ancestor instead (level = that ancestor's level + 1).
    stack: list[tuple[int, str, bool]] = []
    for item, _ in doc.iterate_items():
        if _is_heading_item(item):
            text = _extract_heading_text(item)
            # Noise filters operate on the raw text so exact matches against
            # ``NOISY_TOC_HEADINGS`` ("Note:" vs "Note") keep firing. The
            # normalization below only touches the display form we push
            # onto the stack.
            if text and not _is_noisy_toc_heading(text) and text not in dropped:
                clean_text = normalize_heading_text(text)
                is_numbered = _is_numbered_heading(clean_text)
                if is_numbered:
                    level = infer_heading_level(clean_text)
                else:
                    docling_level = getattr(item, "heading_level", None)
                    if isinstance(docling_level, int) and docling_level > 0:
                        level = docling_level
                    else:
                        # Default: nest under deepest numbered ancestor so the
                        # numbered chapter skeleton is preserved.
                        deepest_numbered = max(
                            (entry[0] for entry in stack if entry[2]),
                            default=0,
                        )
                        level = deepest_numbered + 1 if deepest_numbered else 1
                while stack and stack[-1][0] >= level:
                    stack.pop()
                stack.append((level, clean_text, is_numbered))
        snapshots[_item_key(item)] = [entry[1] for entry in stack]

    return snapshots


def _is_heading_item(item) -> bool:
    label = getattr(item, "label", None)
    if label is None:
        return False
    label_str = getattr(label, "value", None) or str(label)
    return "heading" in label_str.lower() or label_str == "section_header"


def _extract_heading_text(item) -> str:
    if hasattr(item, "text"):
        text = item.text
    elif hasattr(item, "export_to_markdown"):
        text = item.export_to_markdown()
    else:
        text = ""
    return text.strip() if text else ""


def _first_page(item) -> int | None:
    for prov in getattr(item, "prov", []) or []:
        page_no = getattr(prov, "page_no", None)
        if page_no is not None:
            return page_no
    return None


def _is_numbered_heading(text: str) -> bool:
    return HEADING_NUMBER_RE.match(text) is not None


def _is_noisy_toc_heading(text: str) -> bool:
    if text in NOISY_SECTION_IDS or text in NOISY_TOC_HEADINGS:
        return True
    if TABLE_CAPTION_RE.match(text):
        return True
    if _BULLET_HEADING_PREFIX_RE.match(text):
        return True
    for pattern in NOISY_TEXT_PATTERNS:
        if pattern.search(text):
            return True
    return False


def _collect_toc_raw_entries(doc) -> list[dict]:
    """Collect ``(heading, page)`` pairs that pass the base noise filter.

    Shared between :func:`build_toc` and :func:`collect_heading_occurrences`
    so both layers observe the same "candidate heading" set before counting.
    Filters applied here: heading-item check, empty text, ``_is_noisy_toc_heading``
    (NOISY_SECTION_IDS / NOISY_TOC_HEADINGS / table-caption pattern / noisy-text).
    """
    if not hasattr(doc, "iterate_items"):
        return []

    raw: list[dict] = []
    for item, _ in doc.iterate_items():
        if not _is_heading_item(item):
            continue
        text = _extract_heading_text(item)
        if not text:
            continue
        if _is_noisy_toc_heading(text):
            continue
        # Phase 57b: normalize display text after noise filter passes so
        # the TOC / sections layers see identical clean headings ("Including"
        # vs "Including:"). Filtering stays on raw text to preserve exact
        # matches against NOISY_TOC_HEADINGS.
        raw.append({"heading": normalize_heading_text(text), "page": _first_page(item)})
    return raw


def collect_heading_occurrences(doc) -> dict:
    """Count how many times each (non-noise) heading text appears in ``doc``.

    The returned mapping reflects post-noise-filter occurrences so it matches
    the candidate set :func:`build_toc` sees. Used by the converter to derive
    ``dropped_repeat_labels`` once and share it with :func:`build_section_records`.
    """
    return dict(Counter(entry["heading"] for entry in _collect_toc_raw_entries(doc)))


def compute_dropped_repeat_labels(
    occurrences,
    threshold: int = TOC_REPEAT_DROP_THRESHOLD,
) -> set[str]:
    """Return the set of unnumbered headings that repeat more than ``threshold`` times.

    Numbered headings are never dropped — a numbered prefix is a unique
    navigation anchor regardless of literal-text repetition across a doc.
    """
    return {
        heading
        for heading, count in occurrences.items()
        if count > threshold and not _is_numbered_heading(heading)
    }


def build_toc(doc, section_records: list[dict] | None = None) -> list[dict]:
    """Build a pruned hierarchical table of contents from the Docling document.

    Two-pass filter:
    1. Drop headings matching noisy names, noisy patterns, or table captions.
    2. Drop non-numbered headings that repeat more than TOC_REPEAT_DROP_THRESHOLD
       times — they are section-internal labels, not navigation anchors.

    Adds metadata:
    - ``is_chapter``: True for numbered top-level headings (``1 Foo``, ``2 Bar``)
    - ``suspicious``: True when the heading matches a suspicious section
      (heading-detection error from ``flag_suspicious_sections``)
    """
    raw = _collect_toc_raw_entries(doc)
    if not raw:
        return []

    counts = Counter(entry["heading"] for entry in raw)
    dropped = compute_dropped_repeat_labels(counts)
    suspicious_headings = {
        record.get("section_id")
        for record in (section_records or [])
        if record.get("suspicious")
    }

    toc: list[dict] = []
    for entry in raw:
        text = entry["heading"]
        if text in dropped:
            continue
        is_numbered = _is_numbered_heading(text)
        level = infer_heading_level(text)
        record: dict = {
            "heading": text,
            "level": level,
            "page": entry["page"],
            "is_chapter": is_numbered and level == 1,
        }
        if text in suspicious_headings:
            record["suspicious"] = True
        toc.append(record)

    return toc


def build_pages_index(
    chunk_records: list[dict],
    table_records: list[dict],
    alerts: list[dict],
    asset_records: list[dict] | None = None,
) -> list[dict]:
    """Build a page→content reverse index.

    For each page that appears in any record, collect the chunk_ids,
    table_ids, asset_ids, and alert kinds present on that page.

    ``asset_records`` is optional so older callers keep working; when
    provided, each page entry gains an ``asset_ids`` list.
    """
    page_data: dict[int, dict] = {}

    def _ensure_page(page: int) -> dict:
        if page not in page_data:
            page_data[page] = {
                "page": page,
                "chunk_ids": [],
                "table_ids": [],
                "asset_ids": [],
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

    for asset in asset_records or []:
        page = asset.get("page")
        if page is None:
            continue
        entry = _ensure_page(page)
        entry["asset_ids"].append(asset["asset_id"])

    for alert in alerts:
        page = alert.get("page") or alert.get("page_start")
        if page is None:
            continue
        entry = _ensure_page(page)
        kind = alert.get("kind", "unknown")
        if kind not in entry["alert_kinds"]:
            entry["alert_kinds"].append(kind)

    return sorted(page_data.values(), key=lambda x: x["page"])
