import unittest
from pathlib import Path

from docling_bundle.images import resolve_artifacts_dir


class ImagePathTests(unittest.TestCase):
    def test_resolve_artifacts_dir_uses_assets_directory(self):
        document_path = Path("manuals/processed/esp32-s3-datasheet-en/document.md")
        artifacts_dir = resolve_artifacts_dir(document_path)

        self.assertEqual(artifacts_dir, Path("assets"))
