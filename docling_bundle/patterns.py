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
