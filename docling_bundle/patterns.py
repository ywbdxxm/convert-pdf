from __future__ import annotations

import re


TABLE_CAPTION_RE = re.compile(r"^Table\s+\d+(?:-\d+)?\.\s+\S")
IMAGE_REF_RE = re.compile(r"!\[Image\]\(([^)]+)\)")

# Matches numbered heading prefixes like "1", "1.1", "2.3.4", "A.1", "B.2.3"
HEADING_NUMBER_RE = re.compile(
    r"^(?P<prefix>"
    r"[A-Za-z]\.\d+(?:\.\d+)*"  # appendix style: A.1, B.2.3
    r"|"
    r"\d+(?:\.\d+)*"            # numeric style: 1, 2.1, 4.1.3.5
    r")"
    r"(?:\.?\s)"
)

# Docling's layout model occasionally emits "Table"/"Tables" as the split
# pair "T able" / "T ables" when the glyph for the capital T is rendered
# with extra kerning in certain header fonts. Word-boundary anchors keep
# legitimate technical subscript notation ("V flash", "A boot", "T ype",
# "T otal") untouched.
OCR_TABLE_SPLIT_RE = re.compile(r"\bT (ables?)\b")


def clean_ocr_text(text):
    """Normalize chunk / markdown text by reversing known-safe OCR artifacts.

    Currently only reverses the Docling ``T able`` / ``T ables`` split-word
    pattern. Pass-through for ``None`` (caller may hand us absent fields).
    """
    if text is None:
        return None
    if not text:
        return text
    return OCR_TABLE_SPLIT_RE.sub(r"T\1", text)


# Trailing punctuation heading-text normalization (Phase 57b). Docling
# promotes "Including:" / "Features:" / "Parameters," style lines into
# section headings. The colon/comma/semicolon is typographic noise — real
# navigation anchors don't end in punctuation. The trailing period is
# preserved so numbered prefixes like "4.1.1." remain structurally intact
# for downstream parsing.
_HEADING_TRAILING_PUNCT = ":;,"


def normalize_heading_text(text):
    """Strip trailing typographic punctuation from a heading's display text.

    Removes any trailing run of ``:`` / ``;`` / ``,`` (with surrounding
    whitespace). Preserves the trailing ``.`` so numbered headings like
    ``4.1.1.`` keep their structure. Interior punctuation is untouched.

    Returns ``text`` unchanged for empty / None inputs so callers can chain
    this with filter logic.
    """
    if not text:
        return text
    stripped = text.rstrip()
    while stripped and stripped[-1] in _HEADING_TRAILING_PUNCT:
        stripped = stripped[:-1].rstrip()
    return stripped
