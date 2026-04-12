import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from docling_batch.tables import (
    ExportedTable,
    extract_table_caption,
    build_table_manifest_records,
    export_tables,
    inject_table_sidecars_into_markdown,
)


class TableExportTests(unittest.TestCase):
    def test_extract_table_caption_reads_plain_title_line(self):
        caption = extract_table_caption(
            "Table 5-1. Absolute Maximum Ratings\n\n| Symbol | Max |",
            "<table></table>",
        )

        self.assertEqual(caption, "Table 5-1. Absolute Maximum Ratings")

    def test_extract_table_caption_recovers_title_from_single_cell_html_table(self):
        caption = extract_table_caption(
            "| Table 2. STM32H742xI/G and STM32H743xI/G features and peripheral counts |\n|---|",
            "<table><tbody><tr><th>Table 2. STM32H742xI/G and STM32H743xI/G features and peripheral counts</th></tr></tbody></table>",
        )

        self.assertEqual(
            caption,
            "Table 2. STM32H742xI/G and STM32H743xI/G features and peripheral counts",
        )

    def test_build_table_manifest_records_includes_sidecar_paths(self):
        record = build_table_manifest_records(
            doc_id="esp32-s3-datasheet-en",
            table_index=1,
            page_start=64,
            page_end=64,
            csv_path=Path("tables/table_0001.csv"),
            html_path=Path("tables/table_0001.html"),
            label="table",
            caption="Table 5-1. Absolute Maximum Ratings",
        )

        self.assertEqual(record["table_id"], "esp32-s3-datasheet-en:table:0001")
        self.assertEqual(record["page_start"], 64)
        self.assertEqual(record["csv_path"], "tables/table_0001.csv")
        self.assertEqual(record["html_path"], "tables/table_0001.html")
        self.assertEqual(record["label"], "table")
        self.assertEqual(record["caption"], "Table 5-1. Absolute Maximum Ratings")

    def test_export_tables_writes_csv_and_html(self):
        class FakeDataFrame:
            def to_csv(self, path, index=False):
                Path(path).write_text("a,b\n1,2\n", encoding="utf-8")

        class FakeTable:
            prov = [SimpleNamespace(page_no=64)]

            def export_to_dataframe(self, doc=None):
                return FakeDataFrame()

            def export_to_html(self, doc=None):
                return "<table><tr><th>Table 5-1. Absolute Maximum Ratings</th></tr></table>"

            def export_to_markdown(self, doc=None):
                return "Table 5-1. Absolute Maximum Ratings\n\n| Symbol | Max |"

        with tempfile.TemporaryDirectory() as tmp_dir:
            tables_dir = Path(tmp_dir) / "tables"
            records = export_tables("esp32", [FakeTable()], tables_dir)

            self.assertEqual(len(records), 1)
            self.assertTrue((tables_dir / "table_0001.csv").exists())
            self.assertTrue((tables_dir / "table_0001.html").exists())
            self.assertEqual(records[0].record["label"], "table")
            self.assertEqual(records[0].record["caption"], "Table 5-1. Absolute Maximum Ratings")

    def test_inject_table_sidecars_into_markdown_appends_links_after_each_matched_table(self):
        markdown = (
            "## Electrical Characteristics\n\n"
            "Table 5-1. Absolute Maximum Ratings\n\n"
            "| Symbol | Min |\n"
            "|--------|-----|\n"
            "| VDD    | 3.0 |\n\n"
            "Text after table.\n"
        )
        exported_tables = [
            ExportedTable(
                record={
                    "table_id": "esp32:table:0001",
                    "page_start": 64,
                    "page_end": 64,
                    "csv_path": "tables/table_0001.csv",
                    "html_path": "tables/table_0001.html",
                    "label": "table",
                    "caption": "Table 5-1. Absolute Maximum Ratings",
                },
                markdown=(
                    "Table 5-1. Absolute Maximum Ratings\n\n"
                    "| Symbol | Min |\n"
                    "|--------|-----|\n"
                    "| VDD    | 3.0 |"
                ),
            )
        ]

        updated = inject_table_sidecars_into_markdown(markdown, exported_tables)

        self.assertIn(
            "Table sidecars: [HTML](tables/table_0001.html) | [CSV](tables/table_0001.csv) | `esp32:table:0001`",
            updated,
        )
        self.assertLess(
            updated.index("| VDD    | 3.0 |"),
            updated.index("Table sidecars: [HTML](tables/table_0001.html)"),
        )

    def test_inject_table_sidecars_into_markdown_appends_appendix_for_unmatched_tables(self):
        markdown = "## Pins\n\nNo inline table here.\n"
        exported_tables = [
            ExportedTable(
                record={
                    "table_id": "esp32:table:0007",
                    "page_start": 13,
                    "page_end": 13,
                    "csv_path": "tables/table_0007.csv",
                    "html_path": "tables/table_0007.html",
                    "label": "table",
                    "caption": "Table 1-1. ESP32-S3 Series Comparison",
                },
                markdown="Table 1-1. ESP32-S3 Series Comparison\n\n| Part | Value |",
            )
        ]

        updated = inject_table_sidecars_into_markdown(markdown, exported_tables)

        self.assertIn("## Table Sidecars Appendix", updated)
        self.assertIn(
            "- p.13 `esp32:table:0007` Table 1-1. ESP32-S3 Series Comparison [HTML](tables/table_0007.html) [CSV](tables/table_0007.csv)",
            updated,
        )
