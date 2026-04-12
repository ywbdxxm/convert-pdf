import unittest

from argparse import Namespace

from docling_batch.cli import build_runtime_config
from docling_batch.config import build_pdf_pipeline_options
from docling.datamodel.pipeline_options import ThreadedPdfPipelineOptions


class ConfigTests(unittest.TestCase):
    def test_build_pdf_pipeline_options_enables_cuda_and_rapidocr(self):
        options = build_pdf_pipeline_options(
            device="cuda",
            enable_ocr=True,
            ocr_engine="rapidocr",
            force_full_page_ocr=False,
            generate_picture_images=True,
            generate_page_images=False,
            image_scale=1.0,
        )

        self.assertEqual(options.accelerator_options.device.value, "cuda")
        self.assertTrue(options.do_ocr)
        self.assertEqual(options.ocr_options.backend, "torch")
        self.assertTrue(options.generate_picture_images)
        self.assertFalse(options.generate_page_images)
        self.assertIsInstance(options, ThreadedPdfPipelineOptions)
        self.assertEqual(options.layout_batch_size, 32)

    def test_runtime_config_defaults_to_image_filter_off(self):
        config = build_runtime_config(
            Namespace(
                input=["manuals/raw"],
                output="manuals/processed",
                page_window_size=250,
                page_window_min_pages=500,
                device="cuda",
                ocr_engine="rapidocr",
                tokenizer="sentence-transformers/all-MiniLM-L6-v2",
                max_chunk_tokens=384,
                image_mode="referenced",
                generate_page_images=False,
                image_scale=2.0,
                image_filter="off",
                no_ocr=True,
                force_full_page_ocr=False,
            )
        )

        self.assertEqual(config.image_filter, "off")
