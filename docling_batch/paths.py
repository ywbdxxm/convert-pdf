from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentPaths:
    doc_dir: Path
    document_json: Path
    document_markdown: Path
    document_html: Path
    readme: Path
    quality_summary: Path
    alerts: Path
    manifest: Path
    sections: Path
    chunks: Path
    tables_index: Path
    pages_dir: Path
    tables_dir: Path
    runtime_dir: Path
    windows_dir: Path


def build_document_paths(output_root: Path, doc_id: str) -> DocumentPaths:
    doc_dir = output_root / "docling_batch" / doc_id
    return DocumentPaths(
        doc_dir=doc_dir,
        document_json=doc_dir / "document.json",
        document_markdown=doc_dir / "document.md",
        document_html=doc_dir / "document.html",
        readme=doc_dir / "README.generated.md",
        quality_summary=doc_dir / "quality-summary.md",
        alerts=doc_dir / "alerts.json",
        manifest=doc_dir / "manifest.json",
        sections=doc_dir / "sections.jsonl",
        chunks=doc_dir / "chunks.jsonl",
        tables_index=doc_dir / "tables.index.jsonl",
        pages_dir=doc_dir / "pages",
        tables_dir=doc_dir / "tables",
        runtime_dir=doc_dir / "runtime",
        windows_dir=doc_dir / "runtime" / "cache",
    )
