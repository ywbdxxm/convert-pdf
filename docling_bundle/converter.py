from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path
from typing import Any

from docling.chunking import HybridChunker
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import DoclingDocument
from docling_core.types.doc.base import ImageRefMode
from docling_core.types.doc import TableItem
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
import pypdfium2 as pdfium
from docling.pipeline.threaded_standard_pdf_pipeline import ThreadedStandardPdfPipeline

from docling_bundle.alerts import detect_markdown_alerts, detect_table_sidecar_alerts
from docling_bundle.assets_index import build_assets_index
from docling_bundle.config import build_pdf_pipeline_options
from docling_bundle.cross_refs import extract_cross_refs
from docling_bundle.images import filter_markdown_image_refs, picture_keep_flags, resolve_artifacts_dir
from docling_bundle.indexing import attach_table_references, build_chunk_records, build_section_records, build_toc, build_pages_index, flag_suspicious_sections
from docling_bundle.models import RuntimeConfig
from docling_bundle.paths import DocumentPaths, build_document_paths
from docling_bundle.reading_bundle import build_readme
from docling_bundle.tables import export_tables, inject_table_sidecars_into_markdown


@dataclass(frozen=True)
class CachedInputMetadata:
    """Metadata about the input document from cache."""
    page_count: int | None


@dataclass(frozen=True)
class CachedConversionResult:
    """Cached conversion result loaded from window cache."""
    status: ConversionStatus
    document: DoclingDocument
    errors: list[str]
    input: CachedInputMetadata


def make_doc_id(path: Path) -> str:
    stem = path.stem.lower()
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in stem)
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")


def discover_pdf_paths(inputs: list[Path]) -> list[Path]:
    pdfs: list[Path] = []
    for path in inputs:
        if path.is_file() and path.suffix.lower() == ".pdf":
            pdfs.append(path)
            continue
        if path.is_dir():
            pdfs.extend(sorted(candidate for candidate in path.rglob("*.pdf") if candidate.is_file()))

    return sorted(
        {path.resolve() for path in pdfs},
        key=lambda path: (path.name.lower(), str(path)),
    )


def compute_page_windows(total_pages: int, page_window_size: int | None) -> list[tuple[int, int]]:
    if total_pages <= 0:
        return []
    if not page_window_size:
        return [(1, total_pages)]

    windows: list[tuple[int, int]] = []
    start = 1
    while start <= total_pages:
        end = min(total_pages, start + page_window_size - 1)
        windows.append((start, end))
        start = end + 1
    return windows


def format_window_progress(
    doc_id: str,
    window_index: int,
    window_count: int,
    page_start: int,
    page_end: int,
) -> str:
    return f"[{doc_id}] window {window_index}/{window_count} pages {page_start}-{page_end}"


def select_page_windows(
    total_pages: int,
    page_window_size: int | None,
    page_window_min_pages: int,
) -> list[tuple[int, int]]:
    if total_pages <= 0:
        return []
    if not page_window_size or total_pages <= page_window_min_pages:
        return [(1, total_pages)]
    return compute_page_windows(total_pages=total_pages, page_window_size=page_window_size)


def aggregate_conversion_statuses(statuses: list[ConversionStatus]) -> ConversionStatus:
    if not statuses:
        return ConversionStatus.FAILURE
    if all(status == ConversionStatus.SUCCESS for status in statuses):
        return ConversionStatus.SUCCESS
    if all(status == ConversionStatus.FAILURE for status in statuses):
        return ConversionStatus.FAILURE
    return ConversionStatus.PARTIAL_SUCCESS


def get_pdf_page_count(source_path: Path) -> int:
    pdf = pdfium.PdfDocument(str(source_path))
    try:
        return len(pdf)
    finally:
        close = getattr(pdf, "close", None)
        if callable(close):
            close()


def relax_hf_tokenizer_limit(tokenizer: HuggingFaceTokenizer, max_tokens: int | None) -> HuggingFaceTokenizer:
    inner = getattr(tokenizer, "tokenizer", None)
    current_limit = getattr(inner, "model_max_length", None)
    if inner is not None and current_limit is not None and max_tokens:
        inner.model_max_length = max(int(current_limit), max_tokens * 8, 32768)
    return tokenizer


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def build_conversion_signature(config: Any) -> str:
    payload = {
        "docling_version": version("docling"),
        "pipeline": ThreadedStandardPdfPipeline.__name__,
        "device": getattr(config, "device", None),
        "enable_ocr": getattr(config, "enable_ocr", None),
        "ocr_engine": getattr(config, "ocr_engine", None),
        "force_full_page_ocr": getattr(config, "force_full_page_ocr", None),
        "generate_picture_images": getattr(config, "generate_picture_images", None),
        "generate_page_images": getattr(config, "generate_page_images", None),
        "image_scale": getattr(config, "image_scale", None),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def build_window_cache_paths(cache_dir: Path, window_index: int, page_start: int, page_end: int) -> tuple[Path, Path]:
    stem = f"window_{window_index:04d}_p{page_start:06d}-{page_end:06d}"
    return cache_dir / f"{stem}.document.json", cache_dir / f"{stem}.meta.json"


def store_window_result(
    cache_dir: Path,
    window_index: int,
    page_start: int,
    page_end: int,
    source_pdf_sha256: str,
    conversion_signature: str,
    result: Any,
) -> None:
    if result.status not in {ConversionStatus.SUCCESS, ConversionStatus.PARTIAL_SUCCESS} or result.document is None:
        return

    cache_dir.mkdir(parents=True, exist_ok=True)
    document_path, meta_path = build_window_cache_paths(cache_dir, window_index, page_start, page_end)
    result.document.save_as_json(document_path)
    write_json(
        meta_path,
        {
            "status": result.status.value if hasattr(result.status, "value") else str(result.status),
            "page_start": page_start,
            "page_end": page_end,
            "source_pdf_sha256": source_pdf_sha256,
            "conversion_signature": conversion_signature,
            "errors": normalize_errors(getattr(result, "errors", None)),
            "input_page_count": getattr(getattr(result, "input", None), "page_count", None),
            "document_json": document_path.name,
        },
    )


def load_cached_window_result(
    cache_dir: Path,
    window_index: int,
    page_start: int,
    page_end: int,
    source_pdf_sha256: str,
    conversion_signature: str,
    input_page_count: int | None,
):
    document_path, meta_path = build_window_cache_paths(cache_dir, window_index, page_start, page_end)
    if not document_path.exists() or not meta_path.exists():
        return None

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    if meta.get("source_pdf_sha256") != source_pdf_sha256:
        return None
    if meta.get("conversion_signature") != conversion_signature:
        return None
    if meta.get("page_start") != page_start or meta.get("page_end") != page_end:
        return None

    status_text = meta.get("status")
    try:
        status = ConversionStatus(status_text)
    except ValueError:
        return None

    if status not in {ConversionStatus.SUCCESS, ConversionStatus.PARTIAL_SUCCESS}:
        return None

    try:
        document = DoclingDocument.model_validate_json(document_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None

    cached_page_count = input_page_count if input_page_count is not None else meta.get("input_page_count")
    return CachedConversionResult(
        status=status,
        document=document,
        errors=meta.get("errors", []),
        input=CachedInputMetadata(page_count=cached_page_count),
    )


def build_converter(config: RuntimeConfig) -> DocumentConverter:
    pipeline_options = build_pdf_pipeline_options(
        device=config.device,
        enable_ocr=config.enable_ocr,
        ocr_engine=config.ocr_engine,
        force_full_page_ocr=config.force_full_page_ocr,
        generate_picture_images=config.generate_picture_images,
        generate_page_images=config.generate_page_images,
        image_scale=config.image_scale,
    )
    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
                pipeline_cls=ThreadedStandardPdfPipeline,
            ),
        }
    )


def build_chunker(config: RuntimeConfig) -> HybridChunker:
    tokenizer = HuggingFaceTokenizer.from_pretrained(
        model_name=config.tokenizer,
        max_tokens=config.max_chunk_tokens,
    )
    tokenizer = relax_hf_tokenizer_limit(tokenizer, max_tokens=config.max_chunk_tokens)
    return HybridChunker(tokenizer=tokenizer)


def normalize_errors(errors: list | None) -> list[str]:
    normalized = []
    for error in errors or []:
        normalized.append(str(error))
    return normalized


_PAGE_FOOTER_NUMBER_RE = re.compile(r"(<!-- page_break -->)\n\n\d{1,3}\n\n")
_OCR_TABLE_SPLIT_RE = re.compile(r"\bT (ables?)\b")


def _clean_markdown_ocr_artifacts(markdown_text: str) -> str:
    """Post-process Docling markdown to remove universally-known OCR artifacts.

    - Strip standalone page-number lines that Docling detects from page footers.
      Pattern: <!-- page_break --> followed by a lone 1-3 digit line.
    - Fix "T able"/"T ables" split-word artifacts where Docling's layout model
      inserts a space between the capital T and the rest of the word. Other
      capital-letter-plus-word pairs (e.g. "V flash", "A boot") are legitimate
      technical subscript notation and must not be touched.
    """
    markdown_text = _PAGE_FOOTER_NUMBER_RE.sub(r"\1\n\n", markdown_text)
    markdown_text = _OCR_TABLE_SPLIT_RE.sub(r"T\1", markdown_text)
    return markdown_text


def build_window_cache_root(output_root: Path) -> Path:
    repo_root = output_root.resolve().parents[1]
    return repo_root / "tmp" / "docling_bundle-cache"


def concatenate_documents(docs: list[DoclingDocument]) -> DoclingDocument | None:
    if not docs:
        return None
    if len(docs) == 1:
        return docs[0]
    return DoclingDocument.concatenate(docs)


def convert_pdf_in_windows(
    source_path: Path,
    converter: DocumentConverter,
    page_window_size: int | None,
    page_window_min_pages: int,
    window_cache_dir: Path | None = None,
    resume_windows: bool = True,
    config: RuntimeConfig | None = None,
) -> list[Any]:
    total_pages = get_pdf_page_count(source_path)
    windows = select_page_windows(
        total_pages=total_pages,
        page_window_size=page_window_size,
        page_window_min_pages=page_window_min_pages,
    )
    results = []
    doc_id = make_doc_id(source_path)
    window_count = len(windows)
    source_pdf_sha256 = sha256_file(source_path) if window_cache_dir is not None else ""
    conversion_signature = build_conversion_signature(config) if window_cache_dir is not None and config is not None else ""
    for window_index, (page_start, page_end) in enumerate(windows, start=1):
        print(
            format_window_progress(
                doc_id=doc_id,
                window_index=window_index,
                window_count=window_count,
                page_start=page_start,
                page_end=page_end,
            ),
            flush=True,
        )
        if window_cache_dir is not None and resume_windows:
            cached_result = load_cached_window_result(
                cache_dir=window_cache_dir,
                window_index=window_index,
                page_start=page_start,
                page_end=page_end,
                source_pdf_sha256=source_pdf_sha256,
                conversion_signature=conversion_signature,
                input_page_count=total_pages,
            )
            if cached_result is not None:
                print(
                    f"[{doc_id}] reuse cached window {window_index}/{window_count} pages {page_start}-{page_end}",
                    flush=True,
                )
                results.append(cached_result)
                continue

        window_results = list(
            converter.convert_all(
                [source_path],
                raises_on_error=False,
                page_range=(page_start, page_end),
            )
        )
        if window_cache_dir is not None:
            for result in window_results:
                store_window_result(
                    cache_dir=window_cache_dir,
                    window_index=window_index,
                    page_start=page_start,
                    page_end=page_end,
                    source_pdf_sha256=source_pdf_sha256,
                    conversion_signature=conversion_signature,
                    result=result,
                )
        results.extend(window_results)

    return results


def export_document_bundle(
    source_path: Path,
    results: list[Any],
    config: RuntimeConfig,
    chunker: HybridChunker,
    paths: DocumentPaths | None = None,
) -> dict:
    doc_id = make_doc_id(source_path)
    paths = paths or build_document_paths(config.output_root, doc_id)
    paths.doc_dir.mkdir(parents=True, exist_ok=True)

    statuses = [result.status for result in results]
    aggregate_status = aggregate_conversion_statuses(statuses)
    successful_docs = [
        result.document
        for result in results
        if result.status in {ConversionStatus.SUCCESS, ConversionStatus.PARTIAL_SUCCESS} and result.document is not None
    ]
    combined_doc = concatenate_documents(successful_docs)
    first_result = results[0]
    all_errors: list[str] = []
    for result in results:
        all_errors.extend(normalize_errors(getattr(result, "errors", None)))

    status = aggregate_status.value if hasattr(aggregate_status, "value") else str(aggregate_status)
    manifest = {
        "doc_id": doc_id,
        "title": source_path.stem,
        "source_pdf_path": str(source_path),
        "source_filename": source_path.name,
        "page_count": getattr(first_result.input, "page_count", None),
        "status": status,
        "errors": all_errors,
        "document_json": paths.document_json.name,
        "document_markdown": paths.document_markdown.name,
        "document_html": paths.document_html.name,
        "readme": paths.readme.name,
        "alerts_path": paths.alerts.name,
        "sections_index": paths.sections.name,
        "chunks_index": paths.chunks.name,
        "tables_index": paths.tables_index.name,
        "tables_dir": paths.tables_dir.name,
        "toc": paths.toc.name,
        "pages_index": paths.pages_index.name,
        "cross_refs": paths.cross_refs.name,
        "assets_index": paths.assets_index.name,
    }

    if aggregate_status not in {ConversionStatus.SUCCESS, ConversionStatus.PARTIAL_SUCCESS} or combined_doc is None:
        write_json(paths.manifest, manifest)
        return manifest

    artifacts_dir = resolve_artifacts_dir(paths.document_markdown)

    combined_doc.save_as_json(paths.document_json, artifacts_dir=artifacts_dir)
    combined_doc.save_as_html(
        paths.document_html,
        artifacts_dir=artifacts_dir,
        image_mode=ImageRefMode(config.image_mode),
    )
    combined_doc.save_as_markdown(
        paths.document_markdown,
        artifacts_dir=artifacts_dir,
        image_mode=ImageRefMode(config.image_mode),
        page_break_placeholder="<!-- page_break -->",
        image_placeholder="<!-- image -->",
    )

    chunks = list(chunker.chunk(combined_doc))
    chunk_records = build_chunk_records(
        doc_id=doc_id,
        chunks=chunks,
        contextualize=chunker.contextualize,
    )
    section_records = build_section_records(doc_id=doc_id, chunk_records=chunk_records)
    flag_suspicious_sections(section_records, page_count=manifest["page_count"])
    tables = [item for item, _level in combined_doc.iterate_items() if isinstance(item, TableItem)]
    exported_tables = export_tables(doc_id=doc_id, tables=tables, tables_dir=paths.tables_dir, doc=combined_doc)
    table_records = [table.record for table in exported_tables]
    attach_table_references(chunk_records, section_records, table_records)
    manifest["table_count"] = len(table_records)
    manifest["chunk_count"] = len(chunk_records)
    manifest["section_count"] = len(section_records)

    markdown_text = paths.document_markdown.read_text(encoding="utf-8")
    if config.image_filter == "heuristic":
        markdown_text = filter_markdown_image_refs(
            markdown_text,
            picture_keep_flags(combined_doc),
        )
    markdown_text = inject_table_sidecars_into_markdown(markdown_text, exported_tables)
    markdown_text = _clean_markdown_ocr_artifacts(markdown_text)
    paths.document_markdown.write_text(markdown_text, encoding="utf-8")
    alerts = detect_markdown_alerts(markdown_text)
    alerts.extend(detect_table_sidecar_alerts(paths.doc_dir, table_records))
    manifest["alert_count"] = len(alerts)
    write_json(paths.alerts, alerts)

    toc = build_toc(combined_doc, section_records=section_records)
    write_json(paths.toc, toc)

    asset_records = build_assets_index(doc_id, markdown_text, paths.doc_dir)
    write_jsonl(paths.assets_index, asset_records)

    pages_index = build_pages_index(chunk_records, table_records, alerts, asset_records)
    write_jsonl(paths.pages_index, pages_index)

    cross_refs = extract_cross_refs(markdown_text, toc=toc, table_records=table_records, chunk_records=chunk_records)
    write_jsonl(paths.cross_refs, cross_refs)

    write_jsonl(paths.chunks, chunk_records)
    write_jsonl(paths.sections, section_records)
    write_jsonl(paths.tables_index, table_records)
    paths.readme.write_text(
        build_readme(
            doc_id=doc_id,
            source_pdf_path=str(source_path),
            page_count=manifest["page_count"],
            table_count=manifest["table_count"],
            alert_count=manifest["alert_count"],
            alerts=alerts,
            document_json=paths.document_json.name,
            document_markdown=paths.document_markdown.name,
            document_html=paths.document_html.name,
            sections_index=paths.sections.name,
            chunks_index=paths.chunks.name,
            tables_index=paths.tables_index.name,
            alerts_path=paths.alerts.name,
            toc=toc,
            table_records=table_records,
            cross_refs=cross_refs,
            toc_path=paths.toc.name,
            pages_index_path=paths.pages_index.name,
            cross_refs_path=paths.cross_refs.name,
            assets_index_path=paths.assets_index.name,
        ),
        encoding="utf-8",
    )
    write_json(paths.manifest, manifest)
    return manifest


def build_run_summary(results: list[dict], output_root: Path) -> dict:
    return {
        "output_root": str(output_root),
        "total_documents": len(results),
        "success_count": sum(1 for item in results if item["status"] == "success"),
        "partial_success_count": sum(1 for item in results if item["status"] == "partial_success"),
        "failure_count": sum(1 for item in results if item["status"] == "failure"),
        "documents": results,
    }


def run_batch(config: RuntimeConfig) -> dict:
    pdf_paths = discover_pdf_paths(config.input_paths)
    config.output_root.mkdir(parents=True, exist_ok=True)

    if not pdf_paths:
        return build_run_summary([], config.output_root)

    converter = build_converter(config)
    chunker = build_chunker(config)
    manifests: list[dict] = []

    for source_path in pdf_paths:
        paths = build_document_paths(config.output_root, make_doc_id(source_path))
        window_cache_dir = None
        if config.resume_windows:
            window_cache_dir = build_window_cache_root(config.output_root) / make_doc_id(source_path)
        results = convert_pdf_in_windows(
            source_path=source_path,
            converter=converter,
            page_window_size=config.page_window_size,
            page_window_min_pages=config.page_window_min_pages,
            window_cache_dir=window_cache_dir,
            resume_windows=config.resume_windows,
            config=config,
        )
        manifests.append(export_document_bundle(source_path, results, config, chunker, paths=paths))

    return build_run_summary(manifests, config.output_root)
