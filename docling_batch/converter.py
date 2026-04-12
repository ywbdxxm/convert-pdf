from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

from docling.chunking import HybridChunker
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc.base import ImageRefMode
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer

from docling_batch.config import build_pdf_pipeline_options
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
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
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


def export_document_bundle(
    source_path: Path,
    result,
    config: RuntimeConfig,
    chunker: HybridChunker,
) -> dict:
    doc_id = make_doc_id(source_path)
    paths = build_document_paths(config.output_root, doc_id)
    paths.doc_dir.mkdir(parents=True, exist_ok=True)

    status = result.status.value if hasattr(result.status, "value") else str(result.status)
    manifest = {
        "doc_id": doc_id,
        "title": source_path.stem,
        "source_pdf_path": str(source_path),
        "source_pdf_sha256": sha256_file(source_path),
        "source_filename": source_path.name,
        "page_count": getattr(result.input, "page_count", None),
        "docling_version": version("docling"),
        "status": status,
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
        "errors": normalize_errors(getattr(result, "errors", None)),
        "document_json": str(paths.document_json),
        "document_markdown": str(paths.document_markdown),
        "sections_index": str(paths.sections),
        "chunks_index": str(paths.chunks),
    }

    if result.status not in {ConversionStatus.SUCCESS, ConversionStatus.PARTIAL_SUCCESS} or result.document is None:
        write_json(paths.manifest, manifest)
        return manifest

    artifacts_dir = paths.doc_dir / "artifacts"

    result.document.save_as_json(paths.document_json, artifacts_dir=artifacts_dir)
    result.document.save_as_markdown(
        paths.document_markdown,
        artifacts_dir=artifacts_dir,
        image_mode=ImageRefMode(config.image_mode),
        page_break_placeholder="<!-- page_break -->",
        image_placeholder="<!-- image -->",
    )

    chunks = list(chunker.chunk(result.document))
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

    for result in converter.convert_all(pdf_paths, raises_on_error=False):
        source_path = Path(result.input.file)
        manifests.append(export_document_bundle(source_path, result, config, chunker))

    return build_run_summary(manifests, config.output_root)
