import unittest

from docling_bundle.cross_refs import extract_cross_refs


class CrossRefsTests(unittest.TestCase):
    def test_extract_cross_refs_basic(self):
        markdown = "See Section 4.1.3.5 for details.\n<!-- page_break -->\nRefer to Table 2-5."
        toc = [{"heading": "4.1.3.5 PMU", "page": 42}]
        table_records = [{"caption": "Table 2-5. Power Modes", "page_start": 23}]

        refs = extract_cross_refs(markdown, toc=toc, table_records=table_records)

        self.assertEqual(len(refs), 2)
        self.assertEqual(refs[0]["kind"], "section")
        self.assertEqual(refs[0]["target"], "4.1.3.5")
        self.assertEqual(refs[0]["source_page"], 1)
        self.assertEqual(refs[0]["target_page"], 42)
        self.assertNotIn("unresolved", refs[0])

        self.assertEqual(refs[1]["kind"], "table")
        self.assertEqual(refs[1]["target"], "2-5")
        self.assertEqual(refs[1]["source_page"], 2)
        self.assertEqual(refs[1]["target_page"], 23)

    def test_extract_cross_refs_adds_source_chunk_id_when_matched(self):
        markdown = "See Section 4.1 for details."
        chunks = [
            {"chunk_id": "doc:0001", "page_start": 1, "page_end": 1, "text": "Intro text"},
            {"chunk_id": "doc:0002", "page_start": 1, "page_end": 1, "text": "See Section 4.1 for details."},
        ]

        refs = extract_cross_refs(markdown, chunk_records=chunks)

        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0]["source_chunk_id"], "doc:0002")

    def test_extract_cross_refs_omits_source_chunk_id_when_no_match(self):
        markdown = "See Section 4.1 for details."
        chunks = [
            {"chunk_id": "doc:0001", "page_start": 1, "page_end": 1, "text": "Unrelated content"},
        ]

        refs = extract_cross_refs(markdown, chunk_records=chunks)

        self.assertEqual(len(refs), 1)
        self.assertNotIn("source_chunk_id", refs[0])

    def test_extract_cross_refs_matches_case_insensitive(self):
        markdown = "see section 4.1 for details."
        chunks = [
            {"chunk_id": "doc:0001", "page_start": 1, "page_end": 1, "text": "SEE SECTION 4.1 FOR DETAILS."},
        ]

        refs = extract_cross_refs(markdown, chunk_records=chunks)

        self.assertEqual(refs[0]["source_chunk_id"], "doc:0001")

    def test_extract_cross_refs_matches_first_chunk_on_page(self):
        markdown = "See Table 2-5."
        chunks = [
            {"chunk_id": "doc:0001", "page_start": 1, "page_end": 1, "text": "See Table 2-5."},
            {"chunk_id": "doc:0002", "page_start": 1, "page_end": 1, "text": "See Table 2-5."},
        ]

        refs = extract_cross_refs(markdown, chunk_records=chunks)

        # First match wins
        self.assertEqual(refs[0]["source_chunk_id"], "doc:0001")


if __name__ == "__main__":
    unittest.main()
