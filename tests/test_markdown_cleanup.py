import unittest

from docling_bundle.converter import _clean_markdown_ocr_artifacts
from docling_bundle.patterns import clean_ocr_text, normalize_heading_text


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

    def test_strips_standalone_contd_on_next_page_paragraph(self):
        # Between continuation tables Docling emits a free-standing
        # "Cont'd on next page" paragraph. Not a heading, so the existing
        # heading-targeted cleanup misses it. Strip it as its own pattern.
        markdown = (
            "| 14 | GPIO9 | IO |\n"
            "| 15 | GPIO10 | IO |\n\n"
            "Cont'd on next page\n\n"
            "<!-- page_break -->\n"
        )

        result = _clean_markdown_ocr_artifacts(markdown)

        self.assertNotIn("Cont'd on next page", result)
        self.assertIn("| 14 | GPIO9 | IO |", result)

    def test_strips_standalone_table_cont_from_previous_page_paragraph(self):
        # "Table 2-2 - cont'd from previous page" is a free-standing
        # paragraph variant Docling emits after a page break.
        markdown = (
            "<!-- page_break -->\n\n"
            "Table 2-2 - cont'd from previous page\n\n"
            "| col | col |\n"
        )

        result = _clean_markdown_ocr_artifacts(markdown)

        self.assertNotIn("cont'd from previous page", result.lower())
        self.assertIn("| col | col |", result)

    def test_preserves_inline_cont_d_on_next_page_mention(self):
        # Must NOT strip inline mentions embedded in prose; only standalone
        # lines qualify. Here the phrase is part of a sentence.
        markdown = (
            "See cont'd on next page subsection in the reference manual.\n"
        )

        result = _clean_markdown_ocr_artifacts(markdown)

        self.assertIn("cont'd on next page", result)


class CleanOcrTextTests(unittest.TestCase):
    """Phase 57a: chunk-level OCR artifact cleanup mirrors markdown-layer cleanup."""

    def test_fixes_t_able_in_prose(self):
        self.assertEqual(
            clean_ocr_text("As shown in T able 1-1 ESP32-S3 Series Comparison"),
            "As shown in Table 1-1 ESP32-S3 Series Comparison",
        )

    def test_fixes_t_ables_plural(self):
        self.assertEqual(
            clean_ocr_text("List of T ables"),
            "List of Tables",
        )

    def test_preserves_capital_letter_plus_word(self):
        # Legitimate subscript notation "V flash" / "A boot" / "T ype" must
        # NOT be altered. Only the specific "T able(s)" word-boundary match.
        for legit in ("V flash", "A boot", "T ype", "T otal", "V supply"):
            self.assertEqual(clean_ocr_text(legit), legit)

    def test_idempotent(self):
        s = "See T able 2-3 and Table 2-4"
        once = clean_ocr_text(s)
        twice = clean_ocr_text(once)
        self.assertEqual(once, twice)
        self.assertEqual(once, "See Table 2-3 and Table 2-4")

    def test_empty_input(self):
        self.assertEqual(clean_ocr_text(""), "")

    def test_none_input_returns_empty_or_raises_consistently(self):
        # Defensive: the helper should handle non-str gracefully when chunk
        # records have missing fields. Accept either empty string or identity
        # return — tests pin current behaviour so regressions surface.
        self.assertEqual(clean_ocr_text(None), None)


class NormalizeHeadingTextTests(unittest.TestCase):
    """Phase 57b: heading display normalization (trailing :,; cleanup)."""

    def test_strips_trailing_colon(self):
        self.assertEqual(normalize_heading_text("Including:"), "Including")

    def test_strips_trailing_semicolon(self):
        self.assertEqual(normalize_heading_text("Features;"), "Features")

    def test_strips_trailing_comma(self):
        self.assertEqual(normalize_heading_text("Parameters,"), "Parameters")

    def test_preserves_trailing_period_to_avoid_breaking_numbered(self):
        # Numbered heading like "4.1.1." must keep its structure; the
        # sections layer may or may not use the trailing dot but stripping
        # it could break downstream pattern assumptions.
        self.assertEqual(normalize_heading_text("4.1.1."), "4.1.1.")

    def test_preserves_interior_colon(self):
        self.assertEqual(normalize_heading_text("Note: important"), "Note: important")

    def test_strips_trailing_whitespace_before_punctuation(self):
        self.assertEqual(normalize_heading_text("Clock Tree :"), "Clock Tree")

    def test_idempotent(self):
        once = normalize_heading_text("Including:")
        twice = normalize_heading_text(once)
        self.assertEqual(once, twice)

    def test_empty_input(self):
        self.assertEqual(normalize_heading_text(""), "")


if __name__ == "__main__":
    unittest.main()
