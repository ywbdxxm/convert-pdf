import tempfile
import unittest
from pathlib import Path

from docling.datamodel.base_models import ConversionStatus

from docling_batch.converter import (
    aggregate_conversion_statuses,
    compute_page_windows,
    discover_pdf_paths,
    make_doc_id,
    select_page_windows,
)


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

    def test_compute_page_windows_splits_large_documents(self):
        self.assertEqual(
            compute_page_windows(total_pages=501, page_window_size=250),
            [(1, 250), (251, 500), (501, 501)],
        )

    def test_compute_page_windows_returns_single_window_when_disabled(self):
        self.assertEqual(
            compute_page_windows(total_pages=501, page_window_size=None),
            [(1, 501)],
        )

    def test_select_page_windows_keeps_small_documents_whole(self):
        self.assertEqual(
            select_page_windows(total_pages=87, page_window_size=250, page_window_min_pages=500),
            [(1, 87)],
        )

    def test_select_page_windows_splits_only_when_above_threshold(self):
        self.assertEqual(
            select_page_windows(total_pages=501, page_window_size=250, page_window_min_pages=500),
            [(1, 250), (251, 500), (501, 501)],
        )

    def test_aggregate_conversion_statuses_returns_partial_when_any_window_fails(self):
        status = aggregate_conversion_statuses(
            [
                ConversionStatus.SUCCESS,
                ConversionStatus.FAILURE,
                ConversionStatus.SUCCESS,
            ]
        )
        self.assertEqual(status, ConversionStatus.PARTIAL_SUCCESS)
