import unittest

from docling_bundle.reading_bundle import build_readme


def _call(**overrides) -> str:
    defaults = dict(
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
    defaults.update(overrides)
    return build_readme(**defaults)


class DoclingReadingBundleTests(unittest.TestCase):
    def test_build_readme_points_to_key_paths(self):
        text = _call()

        self.assertIn("Start Here", text)
        self.assertIn("Page count: `12`", text)
        self.assertIn("Table count: `5`", text)
        self.assertIn("Alert count: `2`", text)
        self.assertIn("empty_table_sidecar", text)
        self.assertIn("p.42", text)
        self.assertIn("sections.jsonl", text)
        self.assertIn("chunks.jsonl", text)
        self.assertIn("tables.index.jsonl", text)
        self.assertIn("cross_refs.jsonl", text)
        self.assertIn("assets.index.jsonl", text)

    def test_build_readme_omits_chapter_outline_when_no_chapters(self):
        text = _call(toc=[{"heading": "Overview", "level": 1, "page": 1, "is_chapter": False}])

        self.assertNotIn("## Chapter Outline", text)

    def test_build_readme_adds_chapter_outline_when_chapters_exist(self):
        toc = [
            {"heading": "1 Overview", "level": 1, "page": 13, "is_chapter": True},
            {"heading": "1.1 Scope", "level": 2, "page": 13, "is_chapter": False},
            {"heading": "2 Pins", "level": 1, "page": 15, "is_chapter": True},
            {"heading": "3 Boot", "level": 1, "page": 32, "is_chapter": True},
        ]
        text = _call(toc=toc)

        self.assertIn("## Chapter Outline", text)
        self.assertIn("- p.13: 1 Overview", text)
        self.assertIn("- p.15: 2 Pins", text)
        self.assertIn("- p.32: 3 Boot", text)
        # Sub-chapters are NOT in the outline
        self.assertNotIn("1.1 Scope", text.split("## Chapter Outline", 1)[1].split("##", 1)[0])

    def test_build_readme_caps_large_chapter_count(self):
        toc = [
            {"heading": f"{i} Chapter {i}", "level": 1, "page": i, "is_chapter": True}
            for i in range(1, 60)
        ]
        text = _call(toc=toc)

        self.assertIn("(19 more", text)

    def test_build_readme_table_breakdown(self):
        tables = [
            {"table_id": "t1", "kind": "pinout"},
            {"table_id": "t2", "kind": "pinout"},
            {"table_id": "t3", "kind": "electrical"},
            {"table_id": "t4", "kind": "document_index"},  # should be filtered out
            {"table_id": "t5", "kind": "generic"},
        ]
        text = _call(table_records=tables)

        self.assertIn("## Table Breakdown", text)
        self.assertIn("pinout: `2`", text)
        self.assertIn("electrical: `1`", text)
        self.assertIn("generic: `1`", text)
        self.assertNotIn("document_index", text)

    def test_build_readme_omits_table_breakdown_when_only_document_index(self):
        tables = [{"table_id": "t1", "kind": "document_index"}]
        text = _call(table_records=tables)

        self.assertNotIn("## Table Breakdown", text)

    def test_build_readme_cross_refs_summary(self):
        cross_refs = [
            {"kind": "section", "target": "1", "target_page": 13},
            {"kind": "section", "target": "2.1", "target_page": 15},
            {"kind": "table", "target": "2-5", "target_page": 23},
            {"kind": "figure", "target": "3-1", "target_page": None, "unresolved": True},
        ]
        text = _call(cross_refs=cross_refs)

        self.assertIn("## Cross-Reference Summary", text)
        self.assertIn("Total: `4` (resolved: `3`", text)
        self.assertIn("section: `2`", text)
        self.assertIn("table: `1`", text)
        self.assertIn("figure: `1`", text)

    def test_build_readme_alert_includes_fallback_image_path(self):
        alerts = [
            {
                "kind": "table_caption_followed_by_image_without_sidecar",
                "page": 27,
                "caption": "Table 2-9. Peripheral Pin Assignment",
                "image_path": "assets/image_000025_abc.png",
            }
        ]
        text = _call(alerts=alerts, alert_count=1)

        self.assertIn("assets/image_000025_abc.png", text)
        self.assertIn("fallback image", text)


if __name__ == "__main__":
    unittest.main()
