import unittest

from docling_bundle.converter import _clean_markdown_ocr_artifacts


class CleanMarkdownOcrArtifactsTests(unittest.TestCase):
    def test_strips_standalone_page_number_after_page_break(self):
        markdown = (
            "some content\n\n"
            "<!-- page_break -->\n\n"
            "27\n\n"
            "## Next Section\n"
        )

        result = _clean_markdown_ocr_artifacts(markdown)

        self.assertNotIn("\n27\n", result)
        self.assertIn("<!-- page_break -->\n\n## Next Section", result)

    def test_strips_multiple_standalone_page_numbers(self):
        markdown = (
            "<!-- page_break -->\n\n27\n\n## A\n\n"
            "<!-- page_break -->\n\n79\n\n## B\n"
        )

        result = _clean_markdown_ocr_artifacts(markdown)

        self.assertNotIn("27\n", result)
        self.assertNotIn("79\n", result)

    def test_preserves_digits_that_are_not_standalone(self):
        markdown = (
            "<!-- page_break -->\n\n"
            "27 is the page number mentioned inline\n\n"
            "## Section\n"
        )

        result = _clean_markdown_ocr_artifacts(markdown)

        self.assertIn("27 is the page number", result)

    def test_preserves_digits_not_following_page_break(self):
        markdown = "## Chapter\n\n27\n\nContent\n"

        result = _clean_markdown_ocr_artifacts(markdown)

        self.assertIn("27", result)

    def test_fixes_t_able_split_word(self):
        markdown = "As shown in T able 1-1 for details."

        result = _clean_markdown_ocr_artifacts(markdown)

        self.assertEqual(result, "As shown in Table 1-1 for details.")

    def test_fixes_t_ables_split_word(self):
        markdown = "## List of T ables\n"

        result = _clean_markdown_ocr_artifacts(markdown)

        self.assertEqual(result, "## List of Tables\n")

    def test_does_not_touch_legitimate_capital_space_words(self):
        # "F image" = image frequency (RF notation)
        # "V flash" = flash voltage
        # "A boot" = boot current
        markdown = "F = F image + 1 MHz and V flash is 3.3 V while A boot current flows."

        result = _clean_markdown_ocr_artifacts(markdown)

        self.assertIn("F image", result)
        self.assertIn("V flash", result)
        self.assertIn("A boot", result)

    def test_is_idempotent(self):
        markdown = (
            "<!-- page_break -->\n\n27\n\n"
            "As shown in T able 1-1 and List of T ables.\n"
        )

        once = _clean_markdown_ocr_artifacts(markdown)
        twice = _clean_markdown_ocr_artifacts(once)

        self.assertEqual(once, twice)

    def test_strips_standalone_cont_d_from_previous_page_heading(self):
        # Docling OCR promotes the continuation annotation to an H2
        # heading. It is filtered from TOC/sections but remains in
        # document.md and confuses any heading-based navigation.
        markdown = (
            "![Image](assets/foo.png)\n\n"
            "<!-- page_break -->\n\n"
            "## Cont'd from previous page\n\n"
            "| Pin | Name |\n"
            "|-----|------|\n"
            "| 1   | VCC  |\n"
        )

        result = _clean_markdown_ocr_artifacts(markdown)

        self.assertNotIn("## Cont'd from previous page", result)
        # Surrounding structure stays intact.
        self.assertIn("<!-- page_break -->", result)
        self.assertIn("| Pin | Name |", result)
        self.assertIn("![Image](assets/foo.png)", result)

    def test_strips_cont_d_heading_with_level_one(self):
        # Some documents surface it as a single-# heading instead of ##.
        markdown = "<!-- page_break -->\n\n# Cont'd from previous page\n\n| A | B |\n"

        result = _clean_markdown_ocr_artifacts(markdown)

        self.assertNotIn("Cont'd from previous page", result)
        self.assertIn("| A | B |", result)

    def test_strips_cont_d_heading_with_continued_spelling(self):
        # "Continued from previous page" is the long-form variant.
        markdown = "<!-- page_break -->\n\n## Continued from previous page\n\n| A | B |\n"

        result = _clean_markdown_ocr_artifacts(markdown)

        self.assertNotIn("Continued from previous page", result)
        self.assertIn("| A | B |", result)

    def test_preserves_cont_d_text_inside_paragraph(self):
        # Only standalone heading lines are stripped; inline prose mentions
        # must be preserved as a universal safety rule.
        markdown = "The table is cont'd from previous page as usual.\n"

        result = _clean_markdown_ocr_artifacts(markdown)

        self.assertIn("cont'd from previous page", result)


if __name__ == "__main__":
    unittest.main()
