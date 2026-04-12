from __future__ import annotations

import re


TABLE_CAPTION_RE = re.compile(r"^Table\s+\d+(?:-\d+)?\.\s+\S")
IMAGE_REF_RE = re.compile(r"!\[Image\]\(([^)]+)\)")


def _caption_text(line: str) -> str | None:
    normalized = line.strip()
    while normalized.startswith("#"):
        normalized = normalized[1:].strip()
    if normalized.startswith("Table sidecars:"):
        return None
    if TABLE_CAPTION_RE.match(normalized):
        return normalized
    return None


def detect_markdown_alerts(markdown: str) -> list[dict]:
    lines = markdown.splitlines()
    alerts: list[dict] = []
    page = 1
    index = 0

    while index < len(lines):
        line = lines[index].strip()
        if "<!-- page_break -->" in line:
            page += 1
            index += 1
            continue

        caption = _caption_text(line)
        if caption is None:
            index += 1
            continue

        lookahead = index + 1
        found_table_rows = False
        found_sidecar = False
        image_path = None

        while lookahead < len(lines):
            candidate = lines[lookahead].strip()

            if "<!-- page_break -->" in candidate:
                break
            if _caption_text(candidate) is not None:
                break
            if candidate.startswith("## "):
                break
            if not candidate:
                lookahead += 1
                continue
            if candidate.startswith("|"):
                found_table_rows = True
                break
            if candidate.startswith("Table sidecars:"):
                found_sidecar = True
                break
            image_match = IMAGE_REF_RE.search(candidate)
            if image_match:
                image_path = image_match.group(1)
            lookahead += 1

        if image_path and not found_table_rows and not found_sidecar:
            alerts.append(
                {
                    "kind": "table_caption_followed_by_image_without_sidecar",
                    "page": page,
                    "caption": caption,
                    "image_path": image_path,
                }
            )

        index += 1

    return alerts
