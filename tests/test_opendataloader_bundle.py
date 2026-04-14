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

            self.assertTrue((out_dir / "README.generated.md").exists())
            self.assertTrue((out_dir / "manifest.json").exists())
            self.assertTrue((out_dir / "quality-summary.md").exists())

    def test_build_bundle_creates_pages_and_element_index(self):
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
            self.assertTrue((out_dir / "pages" / "page_0002.md").exists())

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

            self.assertTrue((out_dir / "figures" / "image1.png").exists())

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

    def test_build_bundle_cleans_stale_pages_from_previous_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native_dir = root / "native"
            native_dir.mkdir()
            out_dir = root / "bundle"

            (native_dir / "document.json").write_text(
                json.dumps({"kids": [{"type": "paragraph", "page number": 2, "bounding box": [0, 0, 1, 1], "content": "first"}]}),
                encoding="utf-8",
            )
            (native_dir / "document.md").write_text("first\n", encoding="utf-8")
            (native_dir / "document.html").write_text("<p>first</p>", encoding="utf-8")
            build_bundle(
                doc_id="sample-doc",
                source_pdf_path="manuals/raw/example.pdf",
                native_dir=native_dir,
                out_dir=out_dir,
            )
            self.assertTrue((out_dir / "pages" / "page_0002.md").exists())

            (native_dir / "document.json").write_text(json.dumps({"kids": []}), encoding="utf-8")
            build_bundle(
                doc_id="sample-doc",
                source_pdf_path="manuals/raw/example.pdf",
                native_dir=native_dir,
                out_dir=out_dir,
            )

            self.assertFalse((out_dir / "pages" / "page_0002.md").exists())
