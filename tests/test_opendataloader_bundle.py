import json
import tempfile
import unittest
from pathlib import Path

from opendataloader_hybrid.bundle import build_bundle


class OpenDataLoaderBundleTests(unittest.TestCase):
    def test_build_bundle_creates_entry_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native_dir = root / "native"
            native_dir.mkdir()
            (native_dir / "document.json").write_text(json.dumps({"kids": []}), encoding="utf-8")
            (native_dir / "document.md").write_text("# Title\n", encoding="utf-8")
            (native_dir / "document.html").write_text("<h1>Title</h1>", encoding="utf-8")

            out_dir = root / "bundle"
            build_bundle(
                doc_id="sample-doc",
                source_pdf_path="manuals/raw/example.pdf",
                native_dir=native_dir,
                out_dir=out_dir,
            )

            self.assertTrue((out_dir / "README.md").exists())
            self.assertTrue((out_dir / "manifest.json").exists())

    def test_build_bundle_creates_element_index_without_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native_dir = root / "native"
            native_dir.mkdir()
            (native_dir / "document.json").write_text(
                json.dumps(
                    {
                        "kids": [
                            {
                                "type": "paragraph",
                                "page": 2,
                                "bbox": [0, 0, 10, 10],
                                "text": "hello",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (native_dir / "document.md").write_text("hello\n", encoding="utf-8")
            (native_dir / "document.html").write_text("<p>hello</p>", encoding="utf-8")

            out_dir = root / "bundle"
            build_bundle(
                doc_id="sample-doc",
                source_pdf_path="manuals/raw/example.pdf",
                native_dir=native_dir,
                out_dir=out_dir,
            )

            self.assertTrue((out_dir / "elements.index.jsonl").exists())
            self.assertFalse((out_dir / "pages").exists())

    def test_build_bundle_copies_native_image_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native_dir = root / "native"
            native_dir.mkdir()
            (native_dir / "document.json").write_text(json.dumps({"kids": []}), encoding="utf-8")
            (native_dir / "document.md").write_text("hello\n", encoding="utf-8")
            (native_dir / "document.html").write_text("<p>hello</p>", encoding="utf-8")
            image_dir = native_dir / "sample_images"
            image_dir.mkdir()
            (image_dir / "image1.png").write_bytes(b"png")

            out_dir = root / "bundle"
            build_bundle(
                doc_id="sample-doc",
                source_pdf_path="manuals/raw/example.pdf",
                native_dir=native_dir,
                out_dir=out_dir,
            )

            self.assertTrue((out_dir / "assets" / "image1.png").exists())

    def test_build_bundle_rewrites_markdown_image_paths_to_figures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native_dir = root / "native"
            native_dir.mkdir()
            (native_dir / "sample_doc.json").write_text(json.dumps({"kids": []}), encoding="utf-8")
            (native_dir / "sample_doc.md").write_text(
                "![image 1](sample_doc_images/imageFile1.png)\n",
                encoding="utf-8",
            )
            (native_dir / "sample_doc.html").write_text("<p>hello</p>", encoding="utf-8")
            image_dir = native_dir / "sample_doc_images"
            image_dir.mkdir()
            (image_dir / "imageFile1.png").write_bytes(b"png")

            out_dir = root / "bundle"
            build_bundle(
                doc_id="sample-doc",
                source_pdf_path="manuals/raw/vendor/sample_doc.pdf",
                native_dir=native_dir,
                out_dir=out_dir,
            )

            markdown = (out_dir / "document.md").read_text(encoding="utf-8")
            self.assertIn("![image 1](assets/imageFile1.png)", markdown)
            self.assertNotIn("sample_doc_images/", markdown)

    def test_build_bundle_rewrites_html_image_paths_to_figures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native_dir = root / "native"
            native_dir.mkdir()
            (native_dir / "sample_doc.json").write_text(json.dumps({"kids": []}), encoding="utf-8")
            (native_dir / "sample_doc.md").write_text("hello\n", encoding="utf-8")
            (native_dir / "sample_doc.html").write_text(
                '<img src="sample_doc_images/imageFile1.png" alt="figure1">\n',
                encoding="utf-8",
            )
            image_dir = native_dir / "sample_doc_images"
            image_dir.mkdir()
            (image_dir / "imageFile1.png").write_bytes(b"png")

            out_dir = root / "bundle"
            build_bundle(
                doc_id="sample-doc",
                source_pdf_path="manuals/raw/vendor/sample_doc.pdf",
                native_dir=native_dir,
                out_dir=out_dir,
            )

            html = (out_dir / "document.html").read_text(encoding="utf-8")
            self.assertIn('src="assets/imageFile1.png"', html)
            self.assertNotIn("sample_doc_images/", html)

    def test_build_bundle_supports_spaced_metadata_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native_dir = root / "native"
            native_dir.mkdir()
            (native_dir / "document.json").write_text(
                json.dumps(
                    {
                        "kids": [
                            {
                                "type": "paragraph",
                                "page number": 3,
                                "bounding box": [1, 2, 3, 4],
                                "content": "hello from opendataloader",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (native_dir / "document.md").write_text("hello\n", encoding="utf-8")
            (native_dir / "document.html").write_text("<p>hello</p>", encoding="utf-8")

            out_dir = root / "bundle"
            manifest = build_bundle(
                doc_id="sample-doc",
                source_pdf_path="manuals/raw/example.pdf",
                native_dir=native_dir,
                out_dir=out_dir,
            )

            self.assertEqual(manifest["page_count"], 1)
            rows = (out_dir / "elements.index.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertIn('"page": 3', rows[0])
            self.assertIn('"bbox": [1, 2, 3, 4]', rows[0])

    def test_build_bundle_exports_structured_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native_dir = root / "native"
            native_dir.mkdir()
            (native_dir / "document.json").write_text(
                json.dumps(
                    {
                        "kids": [
                            {
                                "type": "table",
                                "page number": 7,
                                "bounding box": [0, 0, 10, 10],
                                "number of rows": 2,
                                "number of columns": 2,
                                "rows": [
                                    {
                                        "type": "table row",
                                        "row number": 1,
                                        "cells": [
                                            {
                                                "type": "table cell",
                                                "row number": 1,
                                                "column number": 1,
                                                "row span": 1,
                                                "column span": 1,
                                                "kids": [{"type": "paragraph", "content": "A"}],
                                            },
                                            {
                                                "type": "table cell",
                                                "row number": 1,
                                                "column number": 2,
                                                "row span": 1,
                                                "column span": 1,
                                                "kids": [{"type": "paragraph", "content": "B"}],
                                            },
                                        ],
                                    },
                                    {
                                        "type": "table row",
                                        "row number": 2,
                                        "cells": [
                                            {
                                                "type": "table cell",
                                                "row number": 2,
                                                "column number": 1,
                                                "row span": 1,
                                                "column span": 1,
                                                "kids": [{"type": "paragraph", "content": "C"}],
                                            },
                                            {
                                                "type": "table cell",
                                                "row number": 2,
                                                "column number": 2,
                                                "row span": 1,
                                                "column span": 1,
                                                "kids": [{"type": "paragraph", "content": "D"}],
                                            },
                                        ],
                                    },
                                ],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (native_dir / "document.md").write_text("hello\n", encoding="utf-8")
            (native_dir / "document.html").write_text("<p>hello</p>", encoding="utf-8")

            out_dir = root / "bundle"
            build_bundle(
                doc_id="sample-doc",
                source_pdf_path="manuals/raw/example.pdf",
                native_dir=native_dir,
                out_dir=out_dir,
            )

            self.assertTrue((out_dir / "tables" / "table_0001.csv").exists())
            self.assertTrue((out_dir / "tables.index.jsonl").exists())
            table_csv = (out_dir / "tables" / "table_0001.csv").read_text(encoding="utf-8")
            self.assertIn("A,B", table_csv)
            self.assertIn("C,D", table_csv)
            readme = (out_dir / "README.md").read_text(encoding="utf-8")
            self.assertIn("Tables index", readme)

    def test_build_bundle_selects_native_files_by_source_stem(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native_dir = root / "native"
            native_dir.mkdir()

            (native_dir / "other_doc.json").write_text(json.dumps({"kids": [{"type": "paragraph", "page number": 1, "content": "wrong"}]}), encoding="utf-8")
            (native_dir / "other_doc.md").write_text("wrong\n", encoding="utf-8")
            (native_dir / "other_doc.html").write_text("<p>wrong</p>", encoding="utf-8")

            (native_dir / "target_doc.json").write_text(json.dumps({"kids": [{"type": "paragraph", "page number": 2, "content": "right"}]}), encoding="utf-8")
            (native_dir / "target_doc.md").write_text("right\n", encoding="utf-8")
            (native_dir / "target_doc.html").write_text("<p>right</p>", encoding="utf-8")

            out_dir = root / "bundle"
            manifest = build_bundle(
                doc_id="target-doc",
                source_pdf_path="manuals/raw/vendor/target_doc.pdf",
                native_dir=native_dir,
                out_dir=out_dir,
            )

            self.assertEqual(manifest["page_count"], 1)
            self.assertEqual(manifest["page_numbers"], [2])
            markdown = (out_dir / "document.md").read_text(encoding="utf-8")
            self.assertIn("right", markdown)
            self.assertFalse((out_dir / "runtime").exists())

    def test_build_bundle_runtime_keeps_only_run_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native_dir = root / "native"
            native_dir.mkdir()

            (native_dir / "sample_doc.json").write_text(json.dumps({"kids": []}), encoding="utf-8")
            (native_dir / "sample_doc.md").write_text("hello\n", encoding="utf-8")
            (native_dir / "sample_doc.html").write_text("<p>hello</p>", encoding="utf-8")
            (native_dir / "run.log").write_text("INFO: Triage summary: JAVA=1, BACKEND=2\n", encoding="utf-8")
            image_dir = native_dir / "sample_doc_images"
            image_dir.mkdir()
            (image_dir / "image1.png").write_bytes(b"png")

            out_dir = root / "bundle"
            build_bundle(
                doc_id="sample-doc",
                source_pdf_path="manuals/raw/vendor/sample_doc.pdf",
                native_dir=native_dir,
                out_dir=out_dir,
            )

            self.assertFalse((out_dir / "runtime").exists())

    def test_build_bundle_writes_runtime_report_from_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native_dir = root / "native"
            native_dir.mkdir()
            (native_dir / "sample_doc.json").write_text(json.dumps({"kids": []}), encoding="utf-8")
            (native_dir / "sample_doc.md").write_text("hello\n", encoding="utf-8")
            (native_dir / "sample_doc.html").write_text("<p>hello</p>", encoding="utf-8")
            (native_dir / "run.log").write_text(
                "INFO: Triage summary: JAVA=18, BACKEND=69\n"
                "WARNING: Backend processing failed: Comparison method violates its general contract!\n"
                "INFO: Falling back to Java processing for backend pages\n",
                encoding="utf-8",
            )

            out_dir = root / "bundle"
            build_bundle(
                doc_id="sample-doc",
                source_pdf_path="manuals/raw/vendor/sample_doc.pdf",
                native_dir=native_dir,
                out_dir=out_dir,
            )

            manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["triage_summary"], "JAVA=18, BACKEND=69")
            self.assertTrue(manifest["fallback_detected"])
            self.assertTrue(manifest["backend_failure_detected"])

    def test_build_bundle_manifest_does_not_expose_native_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native_dir = root / "native"
            native_dir.mkdir()
            (native_dir / "sample_doc.json").write_text(json.dumps({"kids": []}), encoding="utf-8")
            (native_dir / "sample_doc.md").write_text("hello\n", encoding="utf-8")
            (native_dir / "sample_doc.html").write_text("<p>hello</p>", encoding="utf-8")

            out_dir = root / "bundle"
            manifest = build_bundle(
                doc_id="sample-doc",
                source_pdf_path="manuals/raw/vendor/sample_doc.pdf",
                native_dir=native_dir,
                out_dir=out_dir,
            )

            self.assertNotIn("native_dir", manifest)

    def test_build_bundle_emits_alert_for_image_backed_table_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native_dir = root / "native"
            native_dir.mkdir()
            (native_dir / "sample_doc.json").write_text(
                json.dumps(
                    {
                        "kids": [
                            {"type": "heading", "page number": 27, "content": "Table 2-9. Peripheral Pin Assignment"},
                            {"type": "image", "page number": 27, "bounding box": [0, 0, 100, 100]},
                            {"type": "paragraph", "page number": 27, "content": "GPIO0 (P3)"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (native_dir / "sample_doc.md").write_text("hello\n", encoding="utf-8")
            (native_dir / "sample_doc.html").write_text("<p>hello</p>", encoding="utf-8")

            out_dir = root / "bundle"
            build_bundle(
                doc_id="sample-doc",
                source_pdf_path="manuals/raw/vendor/sample_doc.pdf",
                native_dir=native_dir,
                out_dir=out_dir,
            )

            alerts = json.loads((out_dir / "alerts.json").read_text(encoding="utf-8"))
            kinds = {alert["kind"] for alert in alerts}
            self.assertIn("table_heading_with_image_without_native_table", kinds)
