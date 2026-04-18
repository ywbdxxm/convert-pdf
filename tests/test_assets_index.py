import tempfile
import unittest
from pathlib import Path

from docling_bundle.assets_index import build_assets_index


class AssetsIndexTests(unittest.TestCase):
    def _bundle(self, files=None):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        assets = root / "assets"
        assets.mkdir()
        for name, size in (files or {}).items():
            (assets / name).write_bytes(b"\x00" * size)
        return root

    def test_records_page_and_sequence_from_markdown(self):
        markdown = (
            "Intro text\n"
            "![Image](assets/image_000000_a.png)\n"
            "<!-- page_break -->\n"
            "![Image](assets/image_000001_b.png)\n"
            "<!-- page_break -->\n"
            "![Image](assets/image_000002_c.png)\n"
        )
        bundle = self._bundle({"image_000000_a.png": 1000, "image_000001_b.png": 2000, "image_000002_c.png": 3000})

        records = build_assets_index("doc", markdown, bundle)

        self.assertEqual(len(records), 3)
        self.assertEqual(records[0]["page"], 1)
        self.assertEqual(records[1]["page"], 2)
        self.assertEqual(records[2]["page"], 3)
        self.assertEqual([r["asset_id"] for r in records], [
            "doc:asset:0001",
            "doc:asset:0002",
            "doc:asset:0003",
        ])
        self.assertEqual(records[0]["size_bytes"], 1000)
        self.assertEqual(records[0]["path"], "assets/image_000000_a.png")

    def test_records_missing_flag_when_file_absent(self):
        markdown = "![Image](assets/image_ghost.png)\n"
        bundle = self._bundle({})  # no files on disk

        records = build_assets_index("doc", markdown, bundle)

        self.assertEqual(len(records), 1)
        self.assertTrue(records[0].get("missing"))
        self.assertNotIn("size_bytes", records[0])

    def test_md_line_tracks_original_line_number(self):
        markdown = (
            "line 1\n"
            "line 2\n"
            "![Image](assets/a.png)\n"
            "line 4\n"
            "![Image](assets/b.png)\n"
        )
        bundle = self._bundle({"a.png": 10, "b.png": 20})

        records = build_assets_index("doc", markdown, bundle)

        self.assertEqual(records[0]["md_line"], 3)
        self.assertEqual(records[1]["md_line"], 5)

    def test_empty_markdown_returns_empty(self):
        bundle = self._bundle({})
        self.assertEqual(build_assets_index("doc", "", bundle), [])

    def test_markdown_without_images_returns_empty(self):
        bundle = self._bundle({})
        self.assertEqual(
            build_assets_index("doc", "# Header\n\nSome prose.\n", bundle),
            [],
        )

    def test_multiple_images_on_same_page(self):
        markdown = (
            "![Image](assets/a.png)\n"
            "![Image](assets/b.png)\n"
            "![Image](assets/c.png)\n"
            "<!-- page_break -->\n"
            "![Image](assets/d.png)\n"
        )
        bundle = self._bundle({f"{n}.png": 100 for n in "abcd"})

        records = build_assets_index("doc", markdown, bundle)

        pages = [r["page"] for r in records]
        self.assertEqual(pages, [1, 1, 1, 2])


if __name__ == "__main__":
    unittest.main()
