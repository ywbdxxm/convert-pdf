import unittest
from pathlib import Path

from docling_batch.paths import build_document_paths


class BuildDocumentPathsTests(unittest.TestCase):
    def test_document_paths_are_grouped_under_doc_id(self):
        paths = build_document_paths(Path("manuals/processed"), "stm32f4-rm0090")

        self.assertEqual(paths.doc_dir, Path("manuals/processed/stm32f4-rm0090"))
        self.assertEqual(paths.document_json, Path("manuals/processed/stm32f4-rm0090/document.json"))
        self.assertEqual(paths.document_markdown, Path("manuals/processed/stm32f4-rm0090/document.md"))
        self.assertEqual(paths.manifest, Path("manuals/processed/stm32f4-rm0090/manifest.json"))
        self.assertEqual(paths.sections, Path("manuals/processed/stm32f4-rm0090/sections.jsonl"))
        self.assertEqual(paths.chunks, Path("manuals/processed/stm32f4-rm0090/chunks.jsonl"))
