import tempfile
import unittest
from pathlib import Path

from docling_batch.reading_bundle import (
    build_quality_summary,
    build_readme,
    split_markdown_pages,
    write_page_slices,
)


class DoclingReadingBundleTests(unittest.TestCase):
    def test_split_markdown_pages_uses_page_break_placeholders(self):
        markdown = "# Page 1\n\nalpha\n\n<!-- page_break -->\n\n# Page 2\n\nbeta\n"

        pages = split_markdown_pages(markdown)

        self.assertEqual(list(pages.keys()), [1, 2])
        self.assertIn("alpha", pages[1])
        self.assertIn("beta", pages[2])

    def test_write_page_slices_creates_numbered_markdown_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            pages_dir = Path(tmp) / "pages"
            write_page_slices(
                markdown="# First\n\nx\n\n<!-- page_break -->\n\n# Second\n\ny\n",
                pages_dir=pages_dir,
                doc_id="sample-doc",
            )

            self.assertTrue((pages_dir / "page_0001.md").exists())
            self.assertTrue((pages_dir / "page_0002.md").exists())

    def test_build_quality_summary_includes_counts(self):
        text = build_quality_summary(
            doc_id="sample-doc",
            source_pdf_path="manuals/raw/example.pdf",
            page_count=12,
            table_count=5,
            alert_count=2,
            alerts=[{"kind": "empty_table_sidecar"}],
        )

        self.assertIn("Page count: `12`", text)
        self.assertIn("Table count: `5`", text)
        self.assertIn("Alert count: `2`", text)
        self.assertIn("empty_table_sidecar", text)

    def test_build_readme_points_to_key_paths(self):
        text = build_readme(
            doc_id="sample-doc",
            source_pdf_path="manuals/raw/example.pdf",
            document_json="document.json",
            document_markdown="document.md",
            document_html="document.html",
            sections_index="sections.jsonl",
            chunks_index="chunks.jsonl",
            tables_index="tables.index.jsonl",
            alerts_path="alerts.json",
        )

        self.assertIn("Start Here", text)
        self.assertIn("sections.jsonl", text)
        self.assertIn("chunks.jsonl", text)
        self.assertIn("tables.index.jsonl", text)
