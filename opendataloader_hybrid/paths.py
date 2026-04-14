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
    alerts: Path
    elements_index: Path
    tables_index: Path
    tables_dir: Path
    assets_dir: Path
    runtime_dir: Path
    runtime_log: Path
    runtime_report: Path


def build_bundle_paths(root: Path) -> BundlePaths:
    return BundlePaths(
        root=root,
        document_json=root / "document.json",
        document_markdown=root / "document.md",
        document_html=root / "document.html",
        manifest=root / "manifest.json",
        readme=root / "README.md",
        alerts=root / "alerts.json",
        elements_index=root / "elements.index.jsonl",
        tables_index=root / "tables.index.jsonl",
        tables_dir=root / "tables",
        assets_dir=root / "assets",
        runtime_dir=root / "runtime",
        runtime_log=root / "runtime" / "run.log",
        runtime_report=root / "runtime" / "report.json",
    )
