import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from docling_batch.tables import build_table_manifest_records, export_tables


class TableExportTests(unittest.TestCase):
    def test_build_table_manifest_records_includes_sidecar_paths(self):
        record = build_table_manifest_records(
            doc_id="esp32-s3-datasheet-en",
            table_index=1,
            page_start=64,
            page_end=64,
            csv_path=Path("tables/table_0001.csv"),
            html_path=Path("tables/table_0001.html"),
        )

        self.assertEqual(record["table_id"], "esp32-s3-datasheet-en:table:0001")
        self.assertEqual(record["page_start"], 64)
        self.assertEqual(record["csv_path"], "tables/table_0001.csv")
        self.assertEqual(record["html_path"], "tables/table_0001.html")

    def test_export_tables_writes_csv_and_html(self):
        class FakeDataFrame:
            def to_csv(self, path, index=False):
                Path(path).write_text("a,b\n1,2\n", encoding="utf-8")

        class FakeTable:
            prov = [SimpleNamespace(page_no=64)]

            def export_to_dataframe(self, doc=None):
                return FakeDataFrame()

            def export_to_html(self, doc=None):
                return "<table><tr><td>1</td></tr></table>"

        with tempfile.TemporaryDirectory() as tmp_dir:
            tables_dir = Path(tmp_dir) / "tables"
            records = export_tables("esp32", [FakeTable()], tables_dir)

            self.assertEqual(len(records), 1)
            self.assertTrue((tables_dir / "table_0001.csv").exists())
            self.assertTrue((tables_dir / "table_0001.html").exists())
