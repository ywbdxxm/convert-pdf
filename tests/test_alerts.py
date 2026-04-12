import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from docling_batch.alerts import detect_markdown_alerts, detect_table_sidecar_alerts


class MarkdownAlertTests(unittest.TestCase):
    def test_detect_markdown_alerts_flags_caption_followed_by_image_without_sidecar(self):
        markdown = (
            "## 2.3.5 Peripheral Pin Assignment\n\n"
            "## Table 2-9. Peripheral Pin Assignment\n\n"
            "![Image](artifacts/image_000025.png)\n\n"
            "2 Signals can be mapped through GPIO Matrix.\n\n"
            "<!-- page_break -->\n\n"
            "## 2.4 Analog Pins\n"
        )

        alerts = detect_markdown_alerts(markdown)

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["kind"], "table_caption_followed_by_image_without_sidecar")
        self.assertEqual(alerts[0]["page"], 1)
        self.assertEqual(alerts[0]["caption"], "Table 2-9. Peripheral Pin Assignment")
        self.assertEqual(alerts[0]["image_path"], "artifacts/image_000025.png")

    def test_detect_markdown_alerts_ignores_structured_tables_with_sidecars(self):
        markdown = (
            "Table 5-1. Absolute Maximum Ratings\n\n"
            "| Parameter | Min |\n"
            "|-----------|-----|\n"
            "| VDD       | 3.0 |\n\n"
            "Table sidecars: [HTML](tables/table_0031.html) | [CSV](tables/table_0031.csv) | `doc:table:0031`\n"
        )

        alerts = detect_markdown_alerts(markdown)

        self.assertEqual(alerts, [])

    def test_detect_markdown_alerts_ignores_narrative_mentions_of_tables(self):
        markdown = (
            "Table 9 and Table 10 show pin definition and alternate functions.\n\n"
            "![Image](artifacts/image_000075.png)\n"
        )

        alerts = detect_markdown_alerts(markdown)

        self.assertEqual(alerts, [])

    def test_detect_table_sidecar_alerts_flags_empty_sidecar_files(self):
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            tables_dir = root / "tables"
            tables_dir.mkdir()
            (tables_dir / "table_0001.csv").write_text("", encoding="utf-8")
            (tables_dir / "table_0001.html").write_text("<table></table>", encoding="utf-8")
            table_records = [
                {
                    "table_id": "doc:table:0001",
                    "page_start": 42,
                    "page_end": 42,
                    "csv_path": "tables/table_0001.csv",
                    "html_path": "tables/table_0001.html",
                    "caption": "Figure 1. Timing diagram",
                }
            ]

            alerts = detect_table_sidecar_alerts(root, table_records)

            self.assertEqual(len(alerts), 1)
            self.assertEqual(alerts[0]["kind"], "empty_table_sidecar")
            self.assertEqual(alerts[0]["table_id"], "doc:table:0001")
            self.assertTrue(alerts[0]["empty_csv"])
            self.assertFalse(alerts[0]["empty_html"])
