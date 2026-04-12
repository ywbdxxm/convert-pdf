import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from docling.datamodel.base_models import ConversionStatus
from docling_core.types.doc import DoclingDocument

from docling_batch.converter import (
    aggregate_conversion_statuses,
    compute_page_windows,
    convert_pdf_in_windows,
    discover_pdf_paths,
    format_window_progress,
    load_cached_window_result,
    make_doc_id,
    relax_hf_tokenizer_limit,
    select_page_windows,
    store_window_result,
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

    def test_format_window_progress_is_stable_and_human_readable(self):
        message = format_window_progress(
            doc_id="esp32-s3-datasheet-en",
            window_index=2,
            window_count=5,
            page_start=251,
            page_end=500,
        )

        self.assertEqual(
            message,
            "[esp32-s3-datasheet-en] window 2/5 pages 251-500",
        )

    def test_relax_hf_tokenizer_limit_raises_model_max_length(self):
        tokenizer = SimpleNamespace(tokenizer=SimpleNamespace(model_max_length=512))

        updated = relax_hf_tokenizer_limit(tokenizer, max_tokens=384)

        self.assertGreaterEqual(updated.tokenizer.model_max_length, 32768)

    def test_store_and_load_cached_window_result_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_dir = Path(tmp_dir) / "_windows"
            result = SimpleNamespace(
                status=ConversionStatus.SUCCESS,
                document=DoclingDocument(name="window-1"),
                errors=[],
                input=SimpleNamespace(page_count=501),
            )

            store_window_result(
                cache_dir=cache_dir,
                window_index=1,
                page_start=1,
                page_end=250,
                source_pdf_sha256="abc123",
                result=result,
            )

            cached = load_cached_window_result(
                cache_dir=cache_dir,
                window_index=1,
                page_start=1,
                page_end=250,
                source_pdf_sha256="abc123",
                input_page_count=501,
            )

            self.assertIsNotNone(cached)
            self.assertEqual(cached.status, ConversionStatus.SUCCESS)
            self.assertEqual(cached.document.name, "window-1")
            self.assertEqual(cached.input.page_count, 501)

    def test_load_cached_window_result_rejects_stale_source_hash(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_dir = Path(tmp_dir) / "_windows"
            result = SimpleNamespace(
                status=ConversionStatus.SUCCESS,
                document=DoclingDocument(name="window-1"),
                errors=[],
                input=SimpleNamespace(page_count=501),
            )

            store_window_result(
                cache_dir=cache_dir,
                window_index=1,
                page_start=1,
                page_end=250,
                source_pdf_sha256="old-hash",
                result=result,
            )

            cached = load_cached_window_result(
                cache_dir=cache_dir,
                window_index=1,
                page_start=1,
                page_end=250,
                source_pdf_sha256="new-hash",
                input_page_count=501,
            )

            self.assertIsNone(cached)

    def test_convert_pdf_in_windows_reuses_cached_windows_before_calling_converter(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            source_path = root / "large.pdf"
            source_path.write_bytes(b"%PDF-1.4\nplaceholder\n")
            cache_dir = root / "_windows"

            for window_index, page_start, page_end in [
                (1, 1, 250),
                (2, 251, 500),
                (3, 501, 501),
            ]:
                store_window_result(
                    cache_dir=cache_dir,
                    window_index=window_index,
                    page_start=page_start,
                    page_end=page_end,
                    source_pdf_sha256="cached-hash",
                    result=SimpleNamespace(
                        status=ConversionStatus.SUCCESS,
                        document=DoclingDocument(name=f"window-{window_index}"),
                        errors=[],
                        input=SimpleNamespace(page_count=501),
                    ),
                )

            class FailingConverter:
                def convert_all(self, *args, **kwargs):
                    raise AssertionError("converter should not run when every window is cached")

            with patch("docling_batch.converter.get_pdf_page_count", return_value=501), patch(
                "docling_batch.converter.sha256_file", return_value="cached-hash"
            ):
                results = convert_pdf_in_windows(
                    source_path=source_path,
                    converter=FailingConverter(),
                    page_window_size=250,
                    page_window_min_pages=500,
                    window_cache_dir=cache_dir,
                    resume_windows=True,
                )

            self.assertEqual(len(results), 3)
            self.assertEqual([result.document.name for result in results], ["window-1", "window-2", "window-3"])
