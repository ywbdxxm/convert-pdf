import unittest

from docling_bundle.cross_refs import extract_cross_refs


class CrossRefExtractionTests(unittest.TestCase):
    def test_extracts_see_section_with_resolution(self):
        markdown = (
            "Text on page 1\n"
            "<!-- page_break -->\n"
            "For details, see Section 4.1.3.5 Power Management Unit (PMU).\n"
        )
        toc = [{"heading": "4.1.3.5 Power Management Unit (PMU)", "level": 4, "page": 42}]

        refs = extract_cross_refs(markdown, toc=toc)

        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0]["kind"], "section")
        self.assertEqual(refs[0]["target"], "4.1.3.5")
        self.assertEqual(refs[0]["source_page"], 2)
        self.assertEqual(refs[0]["target_page"], 42)
        self.assertNotIn("unresolved", refs[0])

    def test_extracts_see_table_with_resolution(self):
        markdown = "See Table 2-5 for the pin mapping.\n"
        tables = [
            {"caption": "Table 2-5. RTC Peripheral Signals", "page_start": 23, "page_end": 23},
        ]

        refs = extract_cross_refs(markdown, table_records=tables)

        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0]["kind"], "table")
        self.assertEqual(refs[0]["target"], "2-5")
        self.assertEqual(refs[0]["target_page"], 23)

    def test_extracts_see_figure_unresolved(self):
        markdown = "See Figure 3-1 for the overall block diagram.\n"

        refs = extract_cross_refs(markdown)

        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0]["kind"], "figure")
        self.assertEqual(refs[0]["target"], "3-1")
        self.assertTrue(refs[0]["unresolved"])
        self.assertIsNone(refs[0]["target_page"])

    def test_refer_to_section_variant(self):
        markdown = "Refer to Section 2.6 for details.\n"
        toc = [{"heading": "2.6 Pin Mapping", "level": 2, "page": 31}]

        refs = extract_cross_refs(markdown, toc=toc)

        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0]["target"], "2.6")
        self.assertEqual(refs[0]["target_page"], 31)

    def test_handles_ocr_broken_table_t_space_able(self):
        markdown = "See Figure 2-3 and see T able 2-13 for timing reference.\n"
        tables = [
            {"caption": "Table 2-13. Reset Timing", "page_start": 33, "page_end": 33},
        ]

        refs = extract_cross_refs(markdown, table_records=tables)

        kinds = [r["kind"] for r in refs]
        targets = [r["target"] for r in refs]
        self.assertIn("figure", kinds)
        self.assertIn("table", kinds)
        self.assertIn("2-3", targets)
        self.assertIn("2-13", targets)
        table_ref = [r for r in refs if r["kind"] == "table"][0]
        self.assertEqual(table_ref["target_page"], 33)

    def test_does_not_match_bare_table_caption_line(self):
        markdown = "Table 2-5. RTC Peripheral Signals Routed via RTC IO MUX\n"

        refs = extract_cross_refs(markdown)

        self.assertEqual(refs, [])

    def test_unresolved_section_flagged(self):
        markdown = "See Section 9.9.9 for imaginary details.\n"
        toc = [{"heading": "2.1 Pin Layout", "level": 2, "page": 15}]

        refs = extract_cross_refs(markdown, toc=toc)

        self.assertEqual(len(refs), 1)
        self.assertTrue(refs[0]["unresolved"])

    def test_multiple_page_breaks_increment_source_page(self):
        markdown = (
            "p1 content\n"
            "<!-- page_break -->\n"
            "p2 content\n"
            "<!-- page_break -->\n"
            "<!-- page_break -->\n"
            "p4 has see Section 3.2 here.\n"
        )
        toc = [{"heading": "3.2 VDD_SPI Voltage Control", "level": 2, "page": 34}]

        refs = extract_cross_refs(markdown, toc=toc)

        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0]["source_page"], 4)
        self.assertEqual(refs[0]["target_page"], 34)

    def test_empty_markdown(self):
        self.assertEqual(extract_cross_refs(""), [])

    def test_case_insensitive_prefix(self):
        markdown = "See Section 1 and SEE Section 2.1 or see Section 3.\n"
        toc = [
            {"heading": "1 Overview", "level": 1, "page": 13},
            {"heading": "2.1 Pin Layout", "level": 2, "page": 15},
            {"heading": "3 Boot Configurations", "level": 1, "page": 32},
        ]

        refs = extract_cross_refs(markdown, toc=toc)

        self.assertEqual(len(refs), 3)
        self.assertEqual([r["target_page"] for r in refs], [13, 15, 32])


if __name__ == "__main__":
    unittest.main()
