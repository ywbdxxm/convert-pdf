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


if __name__ == "__main__":
    unittest.main()
