from __future__ import annotations

import csv
import json
import re
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


def _resolve_native_file(native_dir: Path, preferred_name: str, suffixes: tuple[str, ...], source_stem: str | None = None) -> Path:
    preferred = native_dir / preferred_name
    if preferred.exists():
        return preferred

    if source_stem:
        for suffix in suffixes:
            candidate = native_dir / f"{source_stem}{suffix}"
            if candidate.exists():
                return candidate

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


def _reset_bundle_root(paths) -> None:
    if not paths.root.exists():
        paths.root.mkdir(parents=True, exist_ok=True)
        return

    for child in paths.root.iterdir():
        if child == paths.runtime_dir:
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

    paths.root.mkdir(parents=True, exist_ok=True)


def _copy_runtime_log(native_dir: Path, runtime_log: Path) -> None:
    runtime_log.parent.mkdir(parents=True, exist_ok=True)
    if runtime_log.exists():
        runtime_log.unlink()
    log_path = native_dir / "run.log"
    if log_path.exists():
        shutil.copy2(log_path, runtime_log)


def _rewrite_media_paths(text: str, source_stem: str) -> str:
    if not text:
        return text

    patterns = [
        rf"{re.escape(source_stem)}_images/",
        rf"{re.escape(source_stem)}_assets/",
    ]
    rewritten = text
    for pattern in patterns:
        rewritten = re.sub(pattern, "assets/", rewritten)
    return rewritten


def _copy_rewritten_text(src: Path, dst: Path, source_stem: str) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    text = src.read_text(encoding="utf-8")
    dst.write_text(_rewrite_media_paths(text, source_stem=source_stem), encoding="utf-8")
    return True


def _parse_runtime_report(native_dir: Path) -> dict:
    report = {
        "log_path": None,
        "triage_summary": None,
        "fallback_detected": False,
        "backend_failure_detected": False,
    }
    log_path = native_dir / "run.log"
    if not log_path.exists():
        return report

    report["log_path"] = str(Path("runtime") / "run.log")
    text = log_path.read_text(encoding="utf-8")
    triage_match = re.search(r"Triage summary:\s*(.+)", text)
    if triage_match:
        report["triage_summary"] = triage_match.group(1).strip()
    if "Falling back to Java processing" in text:
        report["fallback_detected"] = True
    if "Backend processing failed" in text:
        report["backend_failure_detected"] = True
    return report


def _detect_quality_alerts(document: dict, table_records: list[dict], page_numbers: list[int], element_rows: list[dict]) -> list[dict]:
    alerts: list[dict] = []
    if not page_numbers:
        alerts.append({"kind": "no_page_metadata", "detail": "No page metadata found in flattened elements."})
    if not any(row.get("bbox") for row in element_rows):
        alerts.append({"kind": "no_bbox_metadata", "detail": "No bounding boxes found in flattened elements."})

    table_pages = {record["page"] for record in table_records if record.get("page") is not None}
    page_to_headings: dict[int, list[str]] = {}
    page_to_images: dict[int, int] = {}
    for node in document.get("kids", []):
        page = _normalize_page(node.get("page number") or node.get("page"))
        if page is None:
            continue
        if node.get("type") == "heading":
            text = _element_text(node)
            if text:
                page_to_headings.setdefault(page, []).append(text)
        if node.get("type") == "image":
            page_to_images[page] = page_to_images.get(page, 0) + 1

    for page, headings in page_to_headings.items():
        if page in table_pages or page_to_images.get(page, 0) == 0:
            continue
        for heading in headings:
            if heading.lower().startswith("table "):
                alerts.append(
                    {
                        "kind": "table_heading_with_image_without_native_table",
                        "page": page,
                        "detail": heading,
                    }
                )
                break

    return alerts


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


def _collect_text_from_kids(kids) -> str:
    parts: list[str] = []
    for kid in kids or []:
        if isinstance(kid, dict):
            text = _element_text(kid)
            if text:
                parts.append(text)
            child_text = _collect_text_from_kids(kid.get("kids", []))
            if child_text:
                parts.append(child_text)
    return " ".join(part for part in parts if part).strip()


def _export_tables(document: dict, paths, doc_id: str) -> list[dict]:
    table_records: list[dict] = []
    table_index = 0

    for node in document.get("kids", []):
        if node.get("type") != "table":
            continue

        table_index += 1
        row_count = int(node.get("number of rows") or 0)
        col_count = int(node.get("number of columns") or 0)
        if row_count <= 0 or col_count <= 0:
            continue

        matrix = [["" for _ in range(col_count)] for _ in range(row_count)]
        for row in node.get("rows", []) or []:
            for cell in row.get("cells", []) or []:
                row_no = int(cell.get("row number") or 1) - 1
                col_no = int(cell.get("column number") or 1) - 1
                if 0 <= row_no < row_count and 0 <= col_no < col_count:
                    matrix[row_no][col_no] = _collect_text_from_kids(cell.get("kids", []))

        csv_name = f"table_{table_index:04d}.csv"
        csv_path = paths.tables_dir / csv_name
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerows(matrix)

        record = {
            "table_id": f"{doc_id}:table:{table_index:04d}",
            "page": _normalize_page(node.get("page number") or node.get("page")),
            "bbox": _normalize_bbox(node.get("bounding box") or node.get("bbox")),
            "csv_path": str(Path("tables") / csv_name),
            "row_count": row_count,
            "column_count": col_count,
        }
        table_records.append(record)

    _write_jsonl(paths.tables_index, table_records)
    return table_records


def _write_readme(paths, manifest: dict, alerts: list[dict]) -> None:
    lines = [
        f"# {manifest['doc_id']}",
        "",
        "## Summary",
        "",
        f"- Source PDF: `{manifest['source_pdf_path']}`",
        f"- Element count: `{manifest['element_count']}`",
        f"- Pages with extracted elements: `{manifest['page_count']}`",
        f"- Table count: `{manifest['table_count']}`",
        f"- Alert count: `{len(alerts)}`",
        f"- Fallback detected: `{manifest['fallback_detected']}`",
        f"- Triage summary: `{manifest['triage_summary']}`",
        "",
        "## Start Here",
        "",
        "1. Read `document.md` for the broad reading view.",
        "2. Use `elements.index.jsonl` to jump by page/type/bbox-aware elements.",
        "3. Use `tables.index.jsonl` and `tables/` for structured table verification.",
        "4. Return to the original PDF for final engineering verification.",
        "",
        "## Key Files",
        "",
        f"- JSON: `{paths.document_json.name}`",
        f"- Markdown: `{paths.document_markdown.name}`",
        f"- HTML: `{paths.document_html.name}`",
        f"- Elements index: `{paths.elements_index.name}`",
        f"- Tables index: `{paths.tables_index.name}`",
        f"- Alerts: `{paths.alerts.name}`",
    ]
    if alerts:
        lines.extend(["", "## Alerts", ""])
        for alert in alerts:
            suffix = ""
            if alert.get("page") is not None:
                suffix += f" p.{alert['page']}"
            detail = alert.get("detail", "")
            lines.append(f"- {alert['kind']}{suffix}" + (f": {detail}" if detail else ""))
    paths.readme.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_bundle(doc_id: str, source_pdf_path: str, native_dir: Path, out_dir: Path) -> dict:
    paths = build_bundle_paths(out_dir)
    _reset_bundle_root(paths)
    paths.tables_dir.mkdir(parents=True, exist_ok=True)
    paths.assets_dir.mkdir(parents=True, exist_ok=True)

    source_stem = Path(source_pdf_path).stem
    native_json = _resolve_native_file(native_dir, "document.json", (".json",), source_stem=source_stem)
    native_md = _resolve_native_file(native_dir, "document.md", (".md", ".markdown"), source_stem=source_stem)
    native_html = _resolve_native_file(native_dir, "document.html", (".html", ".htm"), source_stem=source_stem)

    _copy_if_exists(native_json, paths.document_json)
    _copy_rewritten_text(native_md, paths.document_markdown, source_stem=source_stem)
    _copy_rewritten_text(native_html, paths.document_html, source_stem=source_stem)

    copied_assets = False
    for dirname, dst in (("tables", paths.tables_dir), ("figures", paths.assets_dir), ("images", paths.assets_dir), ("assets", paths.assets_dir)):
        copied = _copy_tree_if_exists(native_dir / dirname, dst)
        copied_assets = copied_assets or (copied and dst == paths.assets_dir)

    if not copied_assets:
        for child in native_dir.iterdir():
            if child.is_dir() and child.name in {f"{source_stem}_images", f"{source_stem}_assets"}:
                _copy_tree_if_exists(child, paths.assets_dir)
                copied_assets = True
                break

    if not copied_assets:
        for child in native_dir.iterdir():
            if child.is_dir() and child.name.endswith("_images"):
                _copy_tree_if_exists(child, paths.assets_dir)
                copied_assets = True
                break

    document = _read_json(native_json)
    element_rows: list[dict] = []
    _flatten_elements(document.get("kids", []), element_rows)
    indexed_rows = []
    for row in element_rows:
        indexed_rows.append({"doc_id": doc_id, **row})
    _write_jsonl(paths.elements_index, indexed_rows)
    table_records = _export_tables(document=document, paths=paths, doc_id=doc_id)

    page_numbers = sorted({row["page"] for row in indexed_rows if row.get("page") is not None})
    alerts = _detect_quality_alerts(document=document, table_records=table_records, page_numbers=page_numbers, element_rows=indexed_rows)
    runtime_report = _parse_runtime_report(native_dir)

    manifest = {
        "doc_id": doc_id,
        "source_pdf_path": source_pdf_path,
        "element_count": len(indexed_rows),
        "page_count": len(page_numbers),
        "page_numbers": page_numbers,
        "document_json": paths.document_json.name,
        "document_markdown": paths.document_markdown.name,
        "document_html": paths.document_html.name,
        "elements_index": paths.elements_index.name,
        "tables_index": paths.tables_index.name,
        "table_count": len(table_records),
        "alerts_path": paths.alerts.name,
        "fallback_detected": runtime_report["fallback_detected"],
        "backend_failure_detected": runtime_report["backend_failure_detected"],
        "triage_summary": runtime_report["triage_summary"],
    }

    _write_json(paths.manifest, manifest)
    _write_json(paths.alerts, alerts)
    _write_readme(paths, manifest=manifest, alerts=alerts)
    return manifest
