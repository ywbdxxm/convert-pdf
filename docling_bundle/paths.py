from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentPaths:
    doc_dir: Path
    document_json: Path
    document_markdown: Path
    document_html: Path
    readme: Path
    alerts: Path
    manifest: Path
    toc: Path
    pages_index: Path
    sections: Path
    chunks: Path
    tables_index: Path
    tables_dir: Path
    cross_refs: Path
    assets_index: Path


def build_document_paths(output_root: Path, doc_id: str) -> DocumentPaths:
    doc_dir = output_root / "docling_bundle" / doc_id
    return DocumentPaths(
        doc_dir=doc_dir,
        document_json=doc_dir / "document.json",
        document_markdown=doc_dir / "document.md",
        document_html=doc_dir / "document.html",
        readme=doc_dir / "README.md",
        alerts=doc_dir / "alerts.json",
        manifest=doc_dir / "manifest.json",
        toc=doc_dir / "toc.json",
        pages_index=doc_dir / "pages.index.jsonl",
        sections=doc_dir / "sections.jsonl",
        chunks=doc_dir / "chunks.jsonl",
        tables_index=doc_dir / "tables.index.jsonl",
        tables_dir=doc_dir / "tables",
        cross_refs=doc_dir / "cross_refs.jsonl",
        assets_index=doc_dir / "assets.index.jsonl",
    )
