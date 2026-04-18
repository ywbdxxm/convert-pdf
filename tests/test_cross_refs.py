import unittest
from types import SimpleNamespace

from docling_bundle.cross_refs import build_figure_page_map, extract_cross_refs


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


class FigurePageMapTests(unittest.TestCase):
    def _text(self, text, label, page_no):
        return SimpleNamespace(
            text=text,
            label=label,
            prov=[SimpleNamespace(page_no=page_no)],
        )

    def test_build_figure_page_map_from_caption_labeled_text(self):
        """Phase 58b: Docling emits figure titles as ``label="caption"``
        text items with ``prov[0].page_no`` — Docling's native signal,
        not a heuristic. Extract ``{"Figure X-Y": page_no}`` from them."""
        doc = SimpleNamespace(
            texts=[
                self._text("Figure 2-2. ESP32-S3 Power Scheme", "caption", 30),
                self._text("Figure 7-1. QFN56 (7x7 mm) Package", "caption", 77),
                self._text("Figure 1-1. ESP32-S3 Series Nomenclature", "caption", 13),
            ]
        )

        figure_map = build_figure_page_map(doc)

        self.assertEqual(figure_map["Figure 2-2"], 30)
        self.assertEqual(figure_map["Figure 7-1"], 77)
        self.assertEqual(figure_map["Figure 1-1"], 13)

    def test_build_figure_page_map_ignores_non_caption_labels(self):
        """A list_item or paragraph that mentions 'Figure 2-2' in running
        prose is NOT a caption — the map must only use Docling's explicit
        ``label="caption"`` signal, never free-text substring matches."""
        doc = SimpleNamespace(
            texts=[
                self._text(
                    "Each pin's default function is documented in Figure 2-2.",
                    "list_item",
                    15,
                ),
                self._text(
                    "See Figure 2-2 for the power scheme.",
                    "text",
                    10,
                ),
            ]
        )

        self.assertEqual(build_figure_page_map(doc), {})

    def test_build_figure_page_map_ignores_table_captions(self):
        """Caption-labeled text starting with ``Table X-Y`` is a table
        caption — already resolved via tables.index. Figure map must
        only collect entries whose caption text begins with ``Figure``."""
        doc = SimpleNamespace(
            texts=[
                self._text("Table 2-5. Pin Drive Strengths", "caption", 23),
                self._text("Figure 4-1. Address Mapping", "caption", 38),
            ]
        )

        figure_map = build_figure_page_map(doc)

        self.assertNotIn("Table 2-5", figure_map)
        self.assertEqual(figure_map["Figure 4-1"], 38)

    def test_build_figure_page_map_first_caption_wins_on_duplicate(self):
        """If a document somehow has two caption items for the same
        figure id, the first wins — the alternative (overwrite with
        later) could swap to a stale trailing caption."""
        doc = SimpleNamespace(
            texts=[
                self._text("Figure 2-2. Power Scheme", "caption", 30),
                self._text("Figure 2-2. Reprise (cont'd)", "caption", 31),
            ]
        )

        self.assertEqual(build_figure_page_map(doc)["Figure 2-2"], 30)

    def test_build_figure_page_map_tolerates_missing_prov(self):
        """Missing ``prov`` / ``page_no`` — skip entry, don't crash."""
        doc = SimpleNamespace(
            texts=[
                SimpleNamespace(text="Figure 1-1. Nomenclature", label="caption", prov=[]),
                SimpleNamespace(text="Figure 2-2. Power", label="caption", prov=None),
                self._text("Figure 4-1. Address Mapping", "caption", 38),
            ]
        )

        figure_map = build_figure_page_map(doc)

        self.assertNotIn("Figure 1-1", figure_map)
        self.assertNotIn("Figure 2-2", figure_map)
        self.assertEqual(figure_map["Figure 4-1"], 38)

    def test_build_figure_page_map_handles_missing_texts_attribute(self):
        """A doc without ``texts`` (e.g. cache stub) returns empty map
        instead of raising."""
        doc = SimpleNamespace()
        self.assertEqual(build_figure_page_map(doc), {})


class ExtractCrossRefsFigureResolveTests(unittest.TestCase):
    def test_figure_cross_ref_resolves_via_figure_map(self):
        markdown = "The power tree is shown in Figure 2-2 Power Scheme."
        figure_map = {"Figure 2-2": 30}

        refs = extract_cross_refs(markdown, figure_page_map=figure_map)

        self.assertEqual(len(refs), 1)
        ref = refs[0]
        self.assertEqual(ref["kind"], "figure")
        self.assertEqual(ref["target_page"], 30)
        self.assertNotIn("unresolved", ref)

    def test_figure_cross_ref_unresolved_when_not_in_map(self):
        """Regression: absence of a caption entry for the referenced
        figure keeps ``unresolved=True`` — no silent fallback."""
        markdown = "As shown in Figure 9-9 Missing."
        figure_map = {"Figure 2-2": 30}

        refs = extract_cross_refs(markdown, figure_page_map=figure_map)

        self.assertEqual(refs[0]["target_page"], None)
        self.assertTrue(refs[0]["unresolved"])

    def test_figure_cross_ref_falls_back_cleanly_when_no_map_passed(self):
        """Back-compat: callers that don't pass figure_page_map keep
        the old behavior (figure refs stay unresolved)."""
        markdown = "see Figure 3-1 for the strapping timing."

        refs = extract_cross_refs(markdown)

        self.assertEqual(refs[0]["target_page"], None)
        self.assertTrue(refs[0]["unresolved"])


class ExtractCrossRefsTargetIdTests(unittest.TestCase):
    """Phase 59b: cross_refs populate ``target_id`` so agents can jump
    from a reference directly to the target record without re-searching
    by ``caption.startswith("Table X-Y")`` or
    ``section_id.startswith("4.1.3.5")``."""

    def test_section_cross_ref_gets_target_id_from_toc_heading(self):
        markdown = "See Section 4.1.3.5 for PMU details."
        toc = [{"heading": "4.1.3.5 PMU Overview", "page": 42}]

        refs = extract_cross_refs(markdown, toc=toc)

        self.assertEqual(refs[0]["target_id"], "4.1.3.5 PMU Overview")
        self.assertEqual(refs[0]["target_page"], 42)

    def test_section_cross_ref_target_id_matches_exact_target(self):
        """If the TOC heading text equals the target (no trailing
        descriptive words), target_id == target."""
        markdown = "see Section 4"
        toc = [{"heading": "4", "page": 36}]

        refs = extract_cross_refs(markdown, toc=toc)

        self.assertEqual(refs[0]["target_id"], "4")

    def test_section_cross_ref_omits_target_id_when_not_in_toc(self):
        markdown = "see Section 99.9 Nowhere"
        toc = [{"heading": "1 Overview", "page": 1}]

        refs = extract_cross_refs(markdown, toc=toc)

        self.assertNotIn("target_id", refs[0])
        self.assertTrue(refs[0]["unresolved"])

    def test_table_cross_ref_gets_target_id_from_table_records(self):
        markdown = "Refer to Table 2-5 for the modes."
        tables = [
            {
                "table_id": "doc:table:0010",
                "caption": "Table 2-5. Power Modes",
                "page_start": 23,
            }
        ]

        refs = extract_cross_refs(markdown, table_records=tables)

        self.assertEqual(refs[0]["target_id"], "doc:table:0010")
        self.assertEqual(refs[0]["target_page"], 23)

    def test_table_cross_ref_omits_target_id_when_caption_missing(self):
        """If a table record has no caption (uncaptioned table), the
        cross-ref cannot bind to a specific ``table_id`` even if the
        numeric target matches something. Stay conservative."""
        markdown = "see Table 0-0 somewhere"
        tables = [
            {
                "table_id": "doc:table:0015",
                "caption": "",
                "page_start": 22,
            }
        ]

        refs = extract_cross_refs(markdown, table_records=tables)

        self.assertNotIn("target_id", refs[0])

    def test_figure_cross_ref_does_not_get_target_id(self):
        """Docling provides no stable figure id — figure refs resolve
        ``target_page`` via caption map but never get ``target_id``."""
        markdown = "see Figure 2-2 for the scheme"
        figure_map = {"Figure 2-2": 30}

        refs = extract_cross_refs(markdown, figure_page_map=figure_map)

        self.assertEqual(refs[0]["target_page"], 30)
        self.assertNotIn("target_id", refs[0])


if __name__ == "__main__":
    unittest.main()
