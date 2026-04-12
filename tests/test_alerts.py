import unittest

from docling_batch.alerts import detect_markdown_alerts


class MarkdownAlertTests(unittest.TestCase):
    def test_detect_markdown_alerts_flags_caption_followed_by_image_without_sidecar(self):
        markdown = (
            "## 2.3.5 Peripheral Pin Assignment\n\n"
            "Table 2-9. Peripheral Pin Assignment\n\n"
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
