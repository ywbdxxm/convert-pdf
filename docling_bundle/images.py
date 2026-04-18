from __future__ import annotations

import re
from pathlib import Path

from docling_bundle.patterns import IMAGE_REF_RE


def resolve_artifacts_dir(document_path: Path) -> Path:
    del document_path
    return Path("assets")


def _page_dimensions(page) -> tuple[float, float]:
    size = getattr(page, "size", None)
    if size is None:
        return 1.0, 1.0
    width = getattr(size, "width", None)
    height = getattr(size, "height", None)
    if width is not None and height is not None:
        return float(width), float(height)
    if hasattr(size, "as_tuple"):
        width, height = size.as_tuple()
        return float(width), float(height)
    return 1.0, 1.0


def should_keep_picture(
    doc,
    picture,
    *,
    min_area_ratio: float = 0.015,
    tiny_area_ratio: float = 0.01,
    margin_ratio: float = 0.10,
) -> bool:
    prov = (getattr(picture, "prov", None) or [])
    if not prov:
        return True

    captions = getattr(picture, "captions", None) or []
    if len(captions) > 0:
        return True

    first_prov = prov[0]
    page = doc.pages.get(first_prov.page_no) if hasattr(doc, "pages") else None
    if page is None:
        return True

    page_width, page_height = _page_dimensions(page)
    bbox = first_prov.bbox
    width = abs(float(getattr(bbox, "r")) - float(getattr(bbox, "l")))
    height = abs(float(getattr(bbox, "t")) - float(getattr(bbox, "b")))
    area_ratio = (width * height) / max(page_width * page_height, 1.0)

    if area_ratio < tiny_area_ratio:
        return False

    if area_ratio >= min_area_ratio:
        return True

    y_min = min(float(getattr(bbox, "t")), float(getattr(bbox, "b")))
    y_max = max(float(getattr(bbox, "t")), float(getattr(bbox, "b")))
    near_margin = y_min <= page_height * margin_ratio or y_max >= page_height * (1.0 - margin_ratio)

    return not near_margin and area_ratio >= (min_area_ratio / 2.0)


def picture_keep_flags(doc) -> list[bool]:
    flags: list[bool] = []
    if not hasattr(doc, "iterate_items"):
        return flags

    for item, _level in doc.iterate_items():
        if item.__class__.__name__ == "PictureItem":
            flags.append(should_keep_picture(doc, item))
    return flags


def filter_markdown_image_refs(markdown: str, keep_flags: list[bool]) -> str:
    lines = markdown.splitlines()
    filtered: list[str] = []
    image_index = 0

    for line in lines:
        if IMAGE_REF_RE.search(line):
            keep = keep_flags[image_index] if image_index < len(keep_flags) else True
            image_index += 1
            if not keep:
                continue
        filtered.append(line)

    text = "\n".join(filtered)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"
