from __future__ import annotations

import json
import shutil
from pathlib import Path

from .paths import build_bundle_paths


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def _candidate_files(native_dir: Path, suffixes: tuple[str, ...]) -> list[Path]:
    return sorted(path for path in native_dir.iterdir() if path.is_file() and path.suffix.lower() in suffixes)


def _resolve_native_file(native_dir: Path, preferred_name: str, suffixes: tuple[str, ...]) -> Path:
    preferred = native_dir / preferred_name
    if preferred.exists():
        return preferred

    candidates = _candidate_files(native_dir, suffixes)
    if not candidates:
        raise FileNotFoundError(f"no native file found in {native_dir} for suffixes {suffixes}")
    return candidates[0]


def _copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def _copy_tree_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists() or not src.is_dir():
        return False
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return True


def _normalize_page(value) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _normalize_bbox(value):
    if isinstance(value, list) and len(value) == 4:
        return value
    if isinstance(value, dict):
        keys = ["x0", "y0", "x1", "y1"]
        if all(key in value for key in keys):
            return [value[key] for key in keys]
    return None


def _element_text(node: dict) -> str:
    for key in ("text", "content", "alt", "caption", "title"):
        value = node.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _flatten_elements(node, rows: list[dict], parent_id: str = "root", counter: list[int] | None = None) -> None:
    if counter is None:
        counter = [0]

    if isinstance(node, dict):
        counter[0] += 1
        element_id = f"el_{counter[0]:06d}"
        page = _normalize_page(
            node.get("page")
            or node.get("pageNumber")
            or node.get("page_number")
            or node.get("page number")
        )
        bbox = _normalize_bbox(
            node.get("bbox")
            or node.get("boundingBox")
            or node.get("bounding_box")
            or node.get("bounding box")
        )
        text = _element_text(node)
        element_type = node.get("type") or node.get("label") or "unknown"
        rows.append(
            {
                "element_id": element_id,
                "parent_id": parent_id,
                "type": element_type,
                "page": page,
                "bbox": bbox,
                "text": text,
            }
        )
        for child in node.get("kids", []) or []:
            _flatten_elements(child, rows, parent_id=element_id, counter=counter)
        return

    if isinstance(node, list):
        for child in node:
            _flatten_elements(child, rows, parent_id=parent_id, counter=counter)


def _write_page_slices(paths, doc_id: str, element_rows: list[dict]) -> None:
    by_page: dict[int, list[dict]] = {}
    for row in element_rows:
        page = row.get("page")
        if page is None:
            continue
        by_page.setdefault(page, []).append(row)

    paths.pages_dir.mkdir(parents=True, exist_ok=True)
    for page, rows in sorted(by_page.items()):
        page_path = paths.pages_dir / f"page_{page:04d}.md"
        lines = [f"# {doc_id} page {page}", ""]
        for row in rows:
            text = row.get("text") or ""
            bbox = row.get("bbox")
            lines.append(f"- `{row['type']}`" + (f" bbox={bbox}" if bbox else ""))
            if text:
                lines.append(f"  {text}")
        page_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_quality_summary(paths, manifest: dict, alerts: list[dict]) -> None:
    lines = [
        "# Quality Summary",
        "",
        f"- Doc ID: `{manifest['doc_id']}`",
        f"- Source PDF: `{manifest['source_pdf_path']}`",
        f"- Element count: `{manifest['element_count']}`",
        f"- Pages with extracted elements: `{manifest['page_count']}`",
        f"- Alert count: `{len(alerts)}`",
        "",
        "Open `README.generated.md` first, then use `elements.index.jsonl` or `pages/` for targeted inspection.",
    ]
    if alerts:
        lines.extend(["", "## Alerts", ""])
        for alert in alerts:
            lines.append(f"- {alert['kind']}: {alert.get('detail', '')}".rstrip(": "))
    paths.quality_summary.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_readme(paths, manifest: dict) -> None:
    lines = [
        f"# {manifest['doc_id']}",
        "",
        "## Start Here",
        "",
        "1. Read `quality-summary.md`.",
        "2. Read `document.md` for the broad reading view.",
        "3. Use `elements.index.jsonl` to jump by page/type/bbox-aware elements.",
        "4. Use `pages/` when you already know the target page.",
        "5. Return to the original PDF for final engineering verification.",
        "",
        "## Key Paths",
        "",
        f"- Source PDF: `{manifest['source_pdf_path']}`",
        f"- JSON: `{paths.document_json.name}`",
        f"- Markdown: `{paths.document_markdown.name}`",
        f"- HTML: `{paths.document_html.name}`",
        f"- Elements index: `{paths.elements_index.name}`",
        f"- Alerts: `{paths.alerts.name}`",
    ]
    paths.readme.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_bundle(doc_id: str, source_pdf_path: str, native_dir: Path, out_dir: Path) -> dict:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = build_bundle_paths(out_dir)
    paths.pages_dir.mkdir(parents=True, exist_ok=True)
    paths.tables_dir.mkdir(parents=True, exist_ok=True)
    paths.figures_dir.mkdir(parents=True, exist_ok=True)
    paths.runtime_dir.mkdir(parents=True, exist_ok=True)

    native_json = _resolve_native_file(native_dir, "document.json", (".json",))
    native_md = _resolve_native_file(native_dir, "document.md", (".md", ".markdown"))
    native_html = _resolve_native_file(native_dir, "document.html", (".html", ".htm"))

    _copy_if_exists(native_json, paths.document_json)
    _copy_if_exists(native_md, paths.document_markdown)
    _copy_if_exists(native_html, paths.document_html)

    copied_figures = False
    for dirname, dst in (("tables", paths.tables_dir), ("figures", paths.figures_dir), ("images", paths.figures_dir), ("assets", paths.figures_dir)):
        copied = _copy_tree_if_exists(native_dir / dirname, dst)
        copied_figures = copied_figures or (copied and dst == paths.figures_dir)

    if not copied_figures:
        for child in native_dir.iterdir():
            if child.is_dir() and child.name.endswith("_images"):
                _copy_tree_if_exists(child, paths.figures_dir)
                copied_figures = True
                break

    document = _read_json(native_json)
    element_rows: list[dict] = []
    _flatten_elements(document.get("kids", []), element_rows)
    indexed_rows = []
    for row in element_rows:
        indexed_rows.append({"doc_id": doc_id, **row})
    _write_jsonl(paths.elements_index, indexed_rows)
    _write_page_slices(paths, doc_id=doc_id, element_rows=indexed_rows)

    page_numbers = sorted({row["page"] for row in indexed_rows if row.get("page") is not None})
    alerts = []
    if not page_numbers:
        alerts.append({"kind": "no_page_metadata", "detail": "No page metadata found in flattened elements."})
    if not any(row.get("bbox") for row in indexed_rows):
        alerts.append({"kind": "no_bbox_metadata", "detail": "No bounding boxes found in flattened elements."})

    manifest = {
        "doc_id": doc_id,
        "source_pdf_path": source_pdf_path,
        "native_dir": str(native_dir),
        "element_count": len(indexed_rows),
        "page_count": len(page_numbers),
        "page_numbers": page_numbers,
        "document_json": paths.document_json.name,
        "document_markdown": paths.document_markdown.name,
        "document_html": paths.document_html.name,
        "elements_index": paths.elements_index.name,
        "alerts_path": paths.alerts.name,
    }

    _write_json(paths.manifest, manifest)
    _write_json(paths.alerts, alerts)
    _write_quality_summary(paths, manifest=manifest, alerts=alerts)
    _write_readme(paths, manifest=manifest)
    return manifest
