from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

from docling.chunking import HybridChunker
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import DoclingDocument
from docling_core.types.doc.base import ImageRefMode
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
import pypdfium2 as pdfium
from docling.pipeline.threaded_standard_pdf_pipeline import ThreadedStandardPdfPipeline

from docling_batch.config import build_pdf_pipeline_options
from docling_batch.images import filter_markdown_image_refs, picture_keep_flags, resolve_artifacts_dir
from docling_batch.indexing import build_chunk_records, build_section_records
from docling_batch.models import RuntimeConfig
from docling_batch.paths import build_document_paths


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


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
    return HybridChunker(tokenizer=tokenizer)


def normalize_errors(errors) -> list[str]:
    normalized = []
    for error in errors or []:
        normalized.append(str(error))
    return normalized


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
):
    total_pages = get_pdf_page_count(source_path)
    windows = select_page_windows(
        total_pages=total_pages,
        page_window_size=page_window_size,
        page_window_min_pages=page_window_min_pages,
    )
    results = []
    for page_start, page_end in windows:
        results.extend(
            converter.convert_all(
                [source_path],
                raises_on_error=False,
                page_range=(page_start, page_end),
            )
        )

    return results


def export_document_bundle(
    source_path: Path,
    results,
    config: RuntimeConfig,
    chunker: HybridChunker,
) -> dict:
    doc_id = make_doc_id(source_path)
    paths = build_document_paths(config.output_root, doc_id)
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
    windows = []
    all_errors: list[str] = []
    for result in results:
        all_errors.extend(normalize_errors(getattr(result, "errors", None)))
        window_pages = sorted(result.document.pages.keys()) if result.document is not None else []
        windows.append(
            {
                "status": result.status.value if hasattr(result.status, "value") else str(result.status),
                "page_start": window_pages[0] if window_pages else None,
                "page_end": window_pages[-1] if window_pages else None,
                "error_count": len(getattr(result, "errors", None) or []),
            }
        )

    status = aggregate_status.value if hasattr(aggregate_status, "value") else str(aggregate_status)
    manifest = {
        "doc_id": doc_id,
        "title": source_path.stem,
        "source_pdf_path": str(source_path),
        "source_pdf_sha256": sha256_file(source_path),
        "source_filename": source_path.name,
        "page_count": getattr(first_result.input, "page_count", None),
        "docling_version": version("docling"),
        "status": status,
        "page_window_size": config.page_window_size,
        "page_window_min_pages": config.page_window_min_pages,
        "window_count": len(results),
        "windows": windows,
        "ocr_enabled": config.enable_ocr,
        "ocr_engine": config.ocr_engine,
        "force_full_page_ocr": config.force_full_page_ocr,
        "accelerator_device": config.device,
        "chunker_type": "hybrid",
        "tokenizer": config.tokenizer,
        "max_chunk_tokens": config.max_chunk_tokens,
        "image_mode": config.image_mode,
        "generate_picture_images": config.generate_picture_images,
        "generate_page_images": config.generate_page_images,
        "image_scale": config.image_scale,
        "errors": all_errors,
        "document_json": str(paths.document_json),
        "document_markdown": str(paths.document_markdown),
        "sections_index": str(paths.sections),
        "chunks_index": str(paths.chunks),
    }

    if aggregate_status not in {ConversionStatus.SUCCESS, ConversionStatus.PARTIAL_SUCCESS} or combined_doc is None:
        write_json(paths.manifest, manifest)
        return manifest

    artifacts_dir = resolve_artifacts_dir(paths.document_markdown)

    combined_doc.save_as_json(paths.document_json, artifacts_dir=artifacts_dir)
    combined_doc.save_as_markdown(
        paths.document_markdown,
        artifacts_dir=artifacts_dir,
        image_mode=ImageRefMode(config.image_mode),
        page_break_placeholder="<!-- page_break -->",
        image_placeholder="<!-- image -->",
    )
    if config.image_filter == "heuristic":
        filtered_markdown = filter_markdown_image_refs(
            paths.document_markdown.read_text(encoding="utf-8"),
            picture_keep_flags(combined_doc),
        )
        paths.document_markdown.write_text(filtered_markdown, encoding="utf-8")

    chunks = list(chunker.chunk(combined_doc))
    chunk_records = build_chunk_records(
        doc_id=doc_id,
        chunks=chunks,
        contextualize=chunker.contextualize,
    )
    section_records = build_section_records(doc_id=doc_id, chunk_records=chunk_records)

    write_jsonl(paths.chunks, chunk_records)
    write_jsonl(paths.sections, section_records)
    write_json(paths.manifest, manifest)
    return manifest


def build_run_summary(results: list[dict], output_root: Path) -> dict:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    summary = {
        "generated_at": timestamp,
        "output_root": str(output_root),
        "total_documents": len(results),
        "success_count": sum(1 for item in results if item["status"] == "success"),
        "partial_success_count": sum(1 for item in results if item["status"] == "partial_success"),
        "failure_count": sum(1 for item in results if item["status"] == "failure"),
        "documents": results,
    }
    run_path = output_root / "_runs" / f"{timestamp}.json"
    write_json(run_path, summary)
    summary["run_summary_path"] = str(run_path)
    write_json(run_path, summary)
    return summary


def run_batch(config: RuntimeConfig) -> dict:
    pdf_paths = discover_pdf_paths(config.input_paths)
    config.output_root.mkdir(parents=True, exist_ok=True)

    if not pdf_paths:
        return build_run_summary([], config.output_root)

    converter = build_converter(config)
    chunker = build_chunker(config)
    manifests: list[dict] = []

    for source_path in pdf_paths:
        results = convert_pdf_in_windows(
            source_path=source_path,
            converter=converter,
            page_window_size=config.page_window_size,
            page_window_min_pages=config.page_window_min_pages,
        )
        manifests.append(export_document_bundle(source_path, results, config, chunker))

    return build_run_summary(manifests, config.output_root)
