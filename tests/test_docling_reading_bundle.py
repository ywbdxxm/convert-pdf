import unittest

from docling_bundle.reading_bundle import (
    build_readme,
)


class DoclingReadingBundleTests(unittest.TestCase):
    def test_build_readme_points_to_key_paths(self):
        text = build_readme(
            doc_id="sample-doc",
            source_pdf_path="manuals/raw/example.pdf",
            page_count=12,
            table_count=5,
            alert_count=2,
            alerts=[{"kind": "empty_table_sidecar", "page_start": 42, "page_end": 42, "caption": "Example"}],
            document_json="document.json",
            document_markdown="document.md",
            document_html="document.html",
            sections_index="sections.jsonl",
            chunks_index="chunks.jsonl",
            tables_index="tables.index.jsonl",
            alerts_path="alerts.json",
        )

        self.assertIn("Start Here", text)
        self.assertIn("Page count: `12`", text)
        self.assertIn("Table count: `5`", text)
        self.assertIn("Alert count: `2`", text)
        self.assertIn("empty_table_sidecar", text)
        self.assertIn("p.42", text)
        self.assertIn("sections.jsonl", text)
        self.assertIn("chunks.jsonl", text)
        self.assertIn("tables.index.jsonl", text)
