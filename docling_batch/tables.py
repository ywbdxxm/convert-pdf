from __future__ import annotations

from pathlib import Path


def build_table_manifest_records(
    doc_id: str,
    table_index: int,
    page_start: int | None,
    page_end: int | None,
    csv_path: Path,
    html_path: Path,
) -> dict:
    return {
        "table_id": f"{doc_id}:table:{table_index:04d}",
        "page_start": page_start,
        "page_end": page_end,
        "csv_path": str(csv_path),
        "html_path": str(html_path),
    }


def export_tables(doc_id: str, tables, tables_dir: Path, doc=None) -> list[dict]:
    tables_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for index, table in enumerate(tables, start=1):
        csv_name = Path(f"table_{index:04d}.csv")
        html_name = Path(f"table_{index:04d}.html")
        csv_path = tables_dir / csv_name
        html_path = tables_dir / html_name

        dataframe = table.export_to_dataframe(doc=doc)
        dataframe.to_csv(csv_path, index=False)
        html_path.write_text(table.export_to_html(doc=doc), encoding="utf-8")

        pages = [prov.page_no for prov in getattr(table, "prov", []) or [] if getattr(prov, "page_no", None) is not None]
        page_start = min(pages) if pages else None
        page_end = max(pages) if pages else None
        records.append(
            build_table_manifest_records(
                doc_id=doc_id,
                table_index=index,
                page_start=page_start,
                page_end=page_end,
                csv_path=Path("tables") / csv_name,
                html_path=Path("tables") / html_name,
            )
        )

    return records
