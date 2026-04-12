import unittest

from docling_batch.config import build_pdf_pipeline_options


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
