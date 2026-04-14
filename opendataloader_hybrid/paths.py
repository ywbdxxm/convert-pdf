from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BundlePaths:
    root: Path
    document_json: Path
    document_markdown: Path
    document_html: Path
    manifest: Path
    readme: Path
    quality_summary: Path
    alerts: Path
    elements_index: Path
    tables_index: Path
    pages_dir: Path
    tables_dir: Path
    figures_dir: Path
    runtime_dir: Path


def build_bundle_paths(root: Path) -> BundlePaths:
    return BundlePaths(
        root=root,
        document_json=root / "document.json",
        document_markdown=root / "document.md",
        document_html=root / "document.html",
        manifest=root / "manifest.json",
        readme=root / "README.generated.md",
        quality_summary=root / "quality-summary.md",
        alerts=root / "alerts.json",
        elements_index=root / "elements.index.jsonl",
        tables_index=root / "tables.index.jsonl",
        pages_dir=root / "pages",
        tables_dir=root / "tables",
        figures_dir=root / "figures",
        runtime_dir=root / "runtime",
    )
