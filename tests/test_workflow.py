import tempfile
import unittest
from pathlib import Path

from docling_batch.converter import discover_pdf_paths, make_doc_id


class WorkflowHelpersTests(unittest.TestCase):
    def test_make_doc_id_normalizes_filename(self):
        self.assertEqual(make_doc_id(Path("STM32F4 Reference Manual.pdf")), "stm32f4-reference-manual")

    def test_discover_pdf_paths_recurses_and_sorts(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "b.pdf").write_bytes(b"%PDF-1.4\n")
            nested = root / "nested"
            nested.mkdir()
            (nested / "a.pdf").write_bytes(b"%PDF-1.4\n")
            (nested / "ignore.txt").write_text("x", encoding="utf-8")

            paths = discover_pdf_paths([root])

            self.assertEqual(paths, [nested / "a.pdf", root / "b.pdf"])
