import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from docling_bundle.alerts import (
    detect_markdown_alerts,
    detect_missing_caption_alerts,
    detect_table_sidecar_alerts,
)


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
            "Table sidecar: [CSV](tables/table_0031.csv) | `doc:table:0031`\n"
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

    def test_detect_missing_caption_alerts_flags_non_toc_table_without_caption(self):
        """Per 开发要求 rule 5: tables Docling could not caption should
        be surfaced so the agent knows to verify against the source PDF
        instead of trusting a silently-incomplete bundle."""
        table_records = [
            {
                "table_id": "doc:table:0015",
                "page_start": 22,
                "page_end": 22,
                "csv_path": "tables/table_0015.csv",
                "label": "table",
                "caption": "",
                "kind": "pinout",
                "is_toc": False,
            },
            {
                "table_id": "doc:table:0014",
                "page_start": 21,
                "page_end": 21,
                "csv_path": "tables/table_0014.csv",
                "label": "table",
                "caption": "Table 2-4. IO MUX Functions",
                "kind": "pinout",
                "is_toc": False,
            },
        ]

        alerts = detect_missing_caption_alerts(table_records)

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["kind"], "table_without_caption")
        self.assertEqual(alerts[0]["table_id"], "doc:table:0015")
        self.assertEqual(alerts[0]["page_start"], 22)
        self.assertEqual(alerts[0]["csv_path"], "tables/table_0015.csv")

    def test_detect_missing_caption_alerts_ignores_document_index_tables(self):
        """TOC / document_index tables routinely have no caption by design
        (their columns are the TOC entries). They must not trigger the
        quality alert or the alerts list would be dominated by TOC noise."""
        table_records = [
            {
                "table_id": "doc:table:0001",
                "page_start": 7,
                "page_end": 7,
                "csv_path": "tables/table_0001.csv",
                "label": "document_index",
                "caption": "",
                "kind": "document_index",
                "is_toc": True,
            },
        ]

        alerts = detect_missing_caption_alerts(table_records)

        self.assertEqual(alerts, [])

    def test_detect_missing_caption_alerts_ignores_captioned_tables(self):
        table_records = [
            {
                "table_id": "doc:table:0008",
                "page_start": 16,
                "page_end": 16,
                "csv_path": "tables/table_0008.csv",
                "label": "table",
                "caption": "Table 2-1. Pin Overview",
                "kind": "pinout",
                "is_toc": False,
            },
        ]

        alerts = detect_missing_caption_alerts(table_records)

        self.assertEqual(alerts, [])

    def test_detect_table_sidecar_alerts_flags_empty_sidecar_files(self):
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            tables_dir = root / "tables"
            tables_dir.mkdir()
            (tables_dir / "table_0001.csv").write_text("", encoding="utf-8")
            table_records = [
                {
                    "table_id": "doc:table:0001",
                    "page_start": 42,
                    "page_end": 42,
                    "csv_path": "tables/table_0001.csv",
                    "caption": "Figure 1. Timing diagram",
                }
            ]

            alerts = detect_table_sidecar_alerts(root, table_records)

            self.assertEqual(len(alerts), 1)
            self.assertEqual(alerts[0]["kind"], "empty_table_sidecar")
            self.assertEqual(alerts[0]["table_id"], "doc:table:0001")
            self.assertTrue(alerts[0]["empty_csv"])
