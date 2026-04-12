import unittest

from docling_batch.cli import build_parser


class BuildParserTests(unittest.TestCase):
    def test_parser_accepts_input_output_and_gpu_related_flags(self):
        parser = build_parser()

        args = parser.parse_args(
            [
                "convert",
                "--input",
                "manuals/raw",
                "--output",
                "manuals/processed",
                "--device",
                "cuda",
                "--ocr-engine",
                "rapidocr",
                "--tokenizer",
                "sentence-transformers/all-MiniLM-L6-v2",
            ]
        )

        self.assertEqual(args.command, "convert")
        self.assertEqual(args.input, ["manuals/raw"])
        self.assertEqual(args.output, "manuals/processed")
        self.assertEqual(args.device, "cuda")
        self.assertEqual(args.ocr_engine, "rapidocr")
        self.assertEqual(args.tokenizer, "sentence-transformers/all-MiniLM-L6-v2")
        self.assertEqual(args.image_mode, "referenced")
        self.assertFalse(args.generate_page_images)
        self.assertEqual(args.max_chunk_tokens, 384)
        self.assertEqual(args.page_window_min_pages, 500)
        self.assertEqual(args.page_window_size, 250)
        self.assertEqual(args.image_scale, 2.0)
        self.assertEqual(args.image_filter, "off")
