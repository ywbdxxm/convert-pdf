import unittest
from types import SimpleNamespace

from docling_bundle.indexing import (
    attach_table_references,
    build_chunk_record,
    build_chunk_records,
    build_doc_item_lineages,
    build_pages_index,
    build_section_records,
    build_toc,
    collect_heading_occurrences,
    compute_dropped_repeat_labels,
    flag_suspicious_sections,
    infer_heading_level,
    section_key_from_headings,
)


class IndexingTests(unittest.TestCase):
    def test_section_key_from_headings_falls_back_to_root(self):
        self.assertEqual(section_key_from_headings(None), "root")
        self.assertEqual(section_key_from_headings([]), "root")
        self.assertEqual(section_key_from_headings(["Clock", "PLL"]), "Clock / PLL")

    def test_build_chunk_record_uses_page_range_and_contextualized_text(self):
        chunk = SimpleNamespace(
            text="The PLL must be enabled before switching SYSCLK.",
            meta=SimpleNamespace(
                headings=["Clock Control"],
                doc_items=[
                    SimpleNamespace(prov=[SimpleNamespace(page_no=1)]),
                    SimpleNamespace(prov=[SimpleNamespace(page_no=2)]),
                ],
            ),
        )

        record = build_chunk_record(
            doc_id="rm0090",
            chunk_id="rm0090:0001",
            chunk_index=1,
            chunk=chunk,
            contextualized_text="Clock Control\nThe PLL must be enabled before switching SYSCLK.",
        )

        self.assertEqual(record["heading_path"], ["Clock Control"])
        self.assertEqual(record["page_start"], 1)
        self.assertEqual(record["page_end"], 2)
        self.assertEqual(record["citation"], "rm0090 p.1-2")

    def test_build_section_records_aggregates_chunks_by_section(self):
        chunks = [
            {
                "chunk_id": "rm0090:0001",
                "doc_id": "rm0090",
                "section_id": "Clock / PLL",
                "heading_path": ["Clock", "PLL"],
                "page_start": 10,
                "page_end": 10,
                "text": "PLL source selection",
            },
            {
                "chunk_id": "rm0090:0002",
                "doc_id": "rm0090",
                "section_id": "Clock / PLL",
                "heading_path": ["Clock", "PLL"],
                "page_start": 10,
                "page_end": 12,
                "text": "PLL multipliers and divisors",
            },
        ]

        sections = build_section_records("rm0090", chunks)

        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]["section_id"], "Clock / PLL")
        self.assertEqual(sections[0]["page_start"], 10)
        self.assertEqual(sections[0]["page_end"], 12)
        self.assertEqual(sections[0]["chunk_count"], 2)
        self.assertEqual(sections[0]["chunk_ids"], ["rm0090:0001", "rm0090:0002"])

    def test_build_chunk_records_filters_contents_and_continued_page_noise(self):
        chunks = [
            SimpleNamespace(
                text="table of contents body",
                meta=SimpleNamespace(
                    headings=["Contents"],
                    doc_items=[SimpleNamespace(prov=[SimpleNamespace(page_no=7)], label="table")],
                ),
            ),
            SimpleNamespace(
                text="real content",
                meta=SimpleNamespace(
                    headings=["4.1.3.5 Power Management Unit (PMU)"],
                    doc_items=[SimpleNamespace(prov=[SimpleNamespace(page_no=42)], label="text")],
                ),
            ),
            SimpleNamespace(
                text="continued table body",
                meta=SimpleNamespace(
                    headings=["Cont'd from previous page"],
                    doc_items=[SimpleNamespace(prov=[SimpleNamespace(page_no=43)], label="table")],
                ),
            ),
        ]

        records = build_chunk_records(
            doc_id="esp32-s3",
            chunks=chunks,
            contextualize=lambda chunk: chunk.text,
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["section_id"], "4.1.3.5 Power Management Unit (PMU)")

    def test_build_chunk_records_filters_feedback_link_noise(self):
        chunks = [
            SimpleNamespace(
                text="[Submit Documentation Feedback](https://example.com)",
                meta=SimpleNamespace(
                    headings=["5.2 Recommended Operating Conditions"],
                    doc_items=[SimpleNamespace(prov=[SimpleNamespace(page_no=64)], label="text")],
                ),
            ),
            SimpleNamespace(
                text="Operating voltage range is 3.0 V to 3.6 V.",
                meta=SimpleNamespace(
                    headings=["5.2 Recommended Operating Conditions"],
                    doc_items=[SimpleNamespace(prov=[SimpleNamespace(page_no=64)], label="text")],
                ),
            ),
        ]

        records = build_chunk_records(
            doc_id="esp32-s3",
            chunks=chunks,
            contextualize=lambda chunk: chunk.text,
        )

        self.assertEqual(len(records), 1)
        self.assertIn("Operating voltage range", records[0]["text"])

    def test_build_chunk_records_filters_page_number_only_noise(self):
        chunks = [
            SimpleNamespace(
                text="64",
                meta=SimpleNamespace(
                    headings=["5.2 Recommended Operating Conditions"],
                    doc_items=[SimpleNamespace(prov=[SimpleNamespace(page_no=64)], label="text")],
                ),
            ),
            SimpleNamespace(
                text="Power supply voltage VDD3P3_CPU should meet operating conditions.",
                meta=SimpleNamespace(
                    headings=["5.2 Recommended Operating Conditions"],
                    doc_items=[SimpleNamespace(prov=[SimpleNamespace(page_no=64)], label="text")],
                ),
            ),
        ]

        records = build_chunk_records(
            doc_id="esp32-s3",
            chunks=chunks,
            contextualize=lambda chunk: chunk.text,
        )

        self.assertEqual(len(records), 1)
        self.assertIn("Power supply voltage", records[0]["text"])

    def test_attach_table_references_links_chunks_by_page_overlap(self):
        chunk_records = [
            {
                "chunk_id": "esp32:0001",
                "page_start": 64,
                "page_end": 64,
                "section_id": "5.2 Recommended Operating Conditions",
            }
        ]
        section_records = [
            {
                "section_id": "5.2 Recommended Operating Conditions",
                "page_start": 64,
                "page_end": 64,
            }
        ]
        table_records = [
            {
                "table_id": "esp32:table:0001",
                "page_start": 64,
                "page_end": 64,
                "csv_path": "tables/table_0001.csv",
            }
        ]

        attach_table_references(chunk_records, section_records, table_records)

        self.assertEqual(chunk_records[0]["table_ids"], ["esp32:table:0001"])
        self.assertEqual(section_records[0]["table_ids"], ["esp32:table:0001"])


class HeadingLevelTests(unittest.TestCase):
    def test_numbered_heading_single_level(self):
        self.assertEqual(infer_heading_level("1 Overview"), 1)
        self.assertEqual(infer_heading_level("3 Peripherals"), 1)

    def test_numbered_heading_two_levels(self):
        self.assertEqual(infer_heading_level("2.1 Pin Layout"), 2)
        self.assertEqual(infer_heading_level("5.2 Recommended Operating Conditions"), 2)

    def test_numbered_heading_three_levels(self):
        self.assertEqual(infer_heading_level("4.1.3 Clock Control"), 3)

    def test_numbered_heading_four_levels(self):
        self.assertEqual(infer_heading_level("4.1.3.5 Power Management Unit (PMU)"), 4)

    def test_appendix_heading(self):
        self.assertEqual(infer_heading_level("A.1 Appendix Section"), 2)

    def test_unnumbered_heading_defaults_to_1(self):
        self.assertEqual(infer_heading_level("Wi-Fi"), 1)
        self.assertEqual(infer_heading_level("Features"), 1)
        self.assertEqual(infer_heading_level("Note:"), 1)

    def test_empty_heading(self):
        self.assertEqual(infer_heading_level(""), 1)


    def test_build_section_records_includes_chunk_ids(self):
        chunks = [
            {"chunk_id": "doc:0001", "section_id": "1 Overview", "heading_path": ["1 Overview"], "page_start": 1, "page_end": 1, "text": "First chunk"},
            {"chunk_id": "doc:0002", "section_id": "1 Overview", "heading_path": ["1 Overview"], "page_start": 1, "page_end": 2, "text": "Second chunk"},
            {"chunk_id": "doc:0003", "section_id": "2 Pins", "heading_path": ["2 Pins"], "page_start": 3, "page_end": 3, "text": "Third chunk"},
        ]

        sections = build_section_records("doc", chunks)

        overview = [s for s in sections if s["section_id"] == "1 Overview"][0]
        self.assertEqual(overview["chunk_ids"], ["doc:0001", "doc:0002"])
        self.assertEqual(overview["chunk_count"], 2)

        pins = [s for s in sections if s["section_id"] == "2 Pins"][0]
        self.assertEqual(pins["chunk_ids"], ["doc:0003"])
        self.assertEqual(pins["chunk_count"], 1)

    def test_build_section_records_drops_noisy_toc_heading_aggregates(self):
        """Regression: repeated local labels like "Note:" must not become
        ghost sections that aggregate scattered chunks across the document.

        These labels are already filtered from the TOC (build_toc uses
        NOISY_TOC_HEADINGS). sections.jsonl must apply the same filter so
        the two navigation layers stay consistent.
        """
        chunks = [
            # Real section with a proper numbered heading
            {"chunk_id": "doc:0001", "section_id": "2.1 Pin Layout", "heading_path": ["2.1 Pin Layout"], "page_start": 15, "page_end": 15, "text": "Pin layout"},
            # Scattered "Note:" chunks across the document — ghost section
            {"chunk_id": "doc:0002", "section_id": "Note:", "heading_path": ["Note:"], "page_start": 7, "page_end": 7, "text": "First note"},
            {"chunk_id": "doc:0003", "section_id": "Note:", "heading_path": ["Note:"], "page_start": 40, "page_end": 40, "text": "Middle note"},
            {"chunk_id": "doc:0004", "section_id": "Note:", "heading_path": ["Note:"], "page_start": 60, "page_end": 60, "text": "Later note"},
            # Variants we also filter from TOC
            {"chunk_id": "doc:0005", "section_id": "Notes:", "heading_path": ["Notes:"], "page_start": 20, "page_end": 20, "text": "Notes para"},
        ]

        sections = build_section_records("doc", chunks)

        section_ids = {s["section_id"] for s in sections}
        self.assertIn("2.1 Pin Layout", section_ids)
        self.assertNotIn("Note:", section_ids)
        self.assertNotIn("Notes:", section_ids)

    def test_build_section_records_reattaches_dropped_label_chunks_to_previous_section(self):
        """Regression: dropping ghost section labels must not orphan their
        chunks. The bullets under "Feature List" inside "4.2.1.1 UART
        Controller" are structurally part of that UART section — agents
        navigating the section tree must still reach them via UART's
        ``chunk_ids``.

        Rule: when a chunk's section_id is in NOISY_TOC_HEADINGS or
        dropped_repeat_labels, attach it to the most recent kept section
        (preceding it in document order).
        """
        chunks = [
            {"chunk_id": "doc:0010", "section_id": "4.2.1.1 UART", "heading_path": ["4.2.1.1 UART"], "page_start": 51, "page_end": 51, "text": "UART intro"},
            # Ghost-label chunks inside UART
            {"chunk_id": "doc:0011", "section_id": "Feature List", "heading_path": ["Feature List"], "page_start": 51, "page_end": 51, "text": "UART features"},
            {"chunk_id": "doc:0012", "section_id": "Pin Assignment", "heading_path": ["Pin Assignment"], "page_start": 51, "page_end": 51, "text": "UART pins"},
            # Next real section
            {"chunk_id": "doc:0020", "section_id": "4.2.1.2 I2C", "heading_path": ["4.2.1.2 I2C"], "page_start": 52, "page_end": 52, "text": "I2C intro"},
            # Ghost-label chunks inside I2C
            {"chunk_id": "doc:0021", "section_id": "Feature List", "heading_path": ["Feature List"], "page_start": 52, "page_end": 52, "text": "I2C features"},
        ]

        sections = build_section_records(
            "doc",
            chunks,
            dropped_repeat_labels={"Feature List", "Pin Assignment"},
        )

        by_id = {s["section_id"]: s for s in sections}
        self.assertEqual(set(by_id), {"4.2.1.1 UART", "4.2.1.2 I2C"})
        self.assertEqual(
            by_id["4.2.1.1 UART"]["chunk_ids"],
            ["doc:0010", "doc:0011", "doc:0012"],
        )
        self.assertEqual(
            by_id["4.2.1.2 I2C"]["chunk_ids"],
            ["doc:0020", "doc:0021"],
        )

    def test_build_section_records_reattaches_noisy_toc_heading_chunks(self):
        """The same re-parenting rule must apply to NOISY_TOC_HEADINGS
        (``Note:`` / ``Notes:`` / ``Cont'd from previous page``). These are
        section-internal labels: their body text is part of the surrounding
        numbered section, not a standalone scattered Note: section.
        """
        chunks = [
            {"chunk_id": "doc:0001", "section_id": "4.1 System", "heading_path": ["4.1 System"], "page_start": 36, "page_end": 36, "text": "System overview"},
            {"chunk_id": "doc:0002", "section_id": "Note:", "heading_path": ["Note:"], "page_start": 37, "page_end": 37, "text": "Important caveat"},
            {"chunk_id": "doc:0003", "section_id": "4.2 Peripherals", "heading_path": ["4.2 Peripherals"], "page_start": 51, "page_end": 51, "text": "Peripheral intro"},
            {"chunk_id": "doc:0004", "section_id": "Notes:", "heading_path": ["Notes:"], "page_start": 51, "page_end": 51, "text": "Some notes"},
        ]

        sections = build_section_records("doc", chunks)

        by_id = {s["section_id"]: s for s in sections}
        self.assertEqual(set(by_id), {"4.1 System", "4.2 Peripherals"})
        self.assertIn("doc:0002", by_id["4.1 System"]["chunk_ids"])
        self.assertIn("doc:0004", by_id["4.2 Peripherals"]["chunk_ids"])

    def test_build_section_records_reparents_bullet_prefixed_chunks(self):
        """Regression: a chunk whose heading starts with a Unicode bullet glyph
        (e.g. ``· IO MUX:``) must not become a standalone section. The bullet
        was promoted to a heading by Docling's layout analyzer; the chunk body
        still belongs to the preceding numbered section.
        """
        chunks = [
            {"chunk_id": "doc:0001", "section_id": "4.1.3.1 IO MUX and GPIO Matrix", "heading_path": ["4.1.3.1 IO MUX and GPIO Matrix"], "page_start": 40, "page_end": 40, "text": "intro"},
            {"chunk_id": "doc:0002", "section_id": "· IO MUX:", "heading_path": ["· IO MUX:"], "page_start": 40, "page_end": 41, "text": "IO_MUX_GPIO n _REG details"},
            {"chunk_id": "doc:0003", "section_id": "4.1.3.2 Reset", "heading_path": ["4.1.3.2 Reset"], "page_start": 41, "page_end": 41, "text": "Reset section"},
        ]

        sections = build_section_records("doc", chunks)

        section_ids = {s["section_id"] for s in sections}
        self.assertNotIn("· IO MUX:", section_ids)
        self.assertEqual(section_ids, {"4.1.3.1 IO MUX and GPIO Matrix", "4.1.3.2 Reset"})
        by_id = {s["section_id"]: s for s in sections}
        # Orphan chunk re-parents to the preceding numbered section without
        # expanding its page range.
        self.assertIn("doc:0002", by_id["4.1.3.1 IO MUX and GPIO Matrix"]["chunk_ids"])
        self.assertEqual(by_id["4.1.3.1 IO MUX and GPIO Matrix"]["page_start"], 40)
        self.assertEqual(by_id["4.1.3.1 IO MUX and GPIO Matrix"]["page_end"], 40)

    def test_build_section_records_reparents_table_caption_promoted_to_heading(self):
        """Regression: when Docling's layout analyzer promotes a table caption
        like "Table 2-9. Peripheral Pin Assignment" to a heading (typically
        when the table gets rendered as an image and the caption loses its
        normal anchor), sections.jsonl must not expose it as a section.

        ``build_toc`` already filters these via ``TABLE_CAPTION_RE``; sections
        should apply the same rule — re-parent the chunk to the preceding real
        section rather than creating a phantom ``Table X-Y`` section.
        """
        chunks = [
            {"chunk_id": "doc:0001", "section_id": "2.3.5 Peripheral Pin Assignment", "heading_path": ["2.3.5 Peripheral Pin Assignment"], "page_start": 26, "page_end": 26, "text": "intro"},
            {"chunk_id": "doc:0002", "section_id": "Table 2-9. Peripheral Pin Assignment", "heading_path": ["Table 2-9. Peripheral Pin Assignment"], "page_start": 27, "page_end": 27, "text": "note under the table"},
            {"chunk_id": "doc:0003", "section_id": "2.4 Analog Pins", "heading_path": ["2.4 Analog Pins"], "page_start": 28, "page_end": 28, "text": "Analog section"},
        ]

        sections = build_section_records("doc", chunks)

        section_ids = {s["section_id"] for s in sections}
        self.assertEqual(section_ids, {"2.3.5 Peripheral Pin Assignment", "2.4 Analog Pins"})
        by_id = {s["section_id"]: s for s in sections}
        # Orphan chunk re-parents to the preceding real section
        self.assertIn("doc:0002", by_id["2.3.5 Peripheral Pin Assignment"]["chunk_ids"])

    def test_build_section_records_skips_orphan_at_doc_start(self):
        """Edge case: a dropped/noisy chunk at the very beginning of a
        document has no preceding real section to attach to. Such chunks
        are skipped rather than creating a phantom parent.
        """
        chunks = [
            {"chunk_id": "doc:0001", "section_id": "Note:", "heading_path": ["Note:"], "page_start": 1, "page_end": 1, "text": "front-matter note"},
            {"chunk_id": "doc:0002", "section_id": "1 Overview", "heading_path": ["1 Overview"], "page_start": 2, "page_end": 2, "text": "Overview"},
        ]

        sections = build_section_records("doc", chunks)

        section_ids = {s["section_id"] for s in sections}
        self.assertEqual(section_ids, {"1 Overview"})
        # Orphan doc:0001 isn't attached to anything — there is no parent
        self.assertEqual(sections[0]["chunk_ids"], ["doc:0002"])

    def test_build_section_records_drops_repeated_unnumbered_label_ghost_sections(self):
        """Regression (Phase 53): "Feature List" / "Pin Assignment" style
        repeated sub-headings must not become ghost sections that span many
        pages. They are filtered from the TOC via the repeat-count rule; the
        same rule must apply to sections.jsonl to keep both navigation layers
        consistent.

        Without the fix, all scattered "Feature List" chunks (from UART,
        I2C, SPI, etc. sub-blocks) aggregate into one 24-page ghost section.
        """
        chunks = [
            # Real numbered section
            {"chunk_id": "doc:0001", "section_id": "4.2.1.1 UART", "heading_path": ["4.2.1.1 UART"], "page_start": 51, "page_end": 51, "text": "UART intro"},
            # Ghost "Feature List" chunks scattered across the doc
            {"chunk_id": "doc:0002", "section_id": "Feature List", "heading_path": ["Feature List"], "page_start": 36, "page_end": 36, "text": "PIE features"},
            {"chunk_id": "doc:0003", "section_id": "Feature List", "heading_path": ["Feature List"], "page_start": 44, "page_end": 44, "text": "Timer features"},
            {"chunk_id": "doc:0004", "section_id": "Feature List", "heading_path": ["Feature List"], "page_start": 58, "page_end": 58, "text": "PCNT features"},
            {"chunk_id": "doc:0005", "section_id": "Feature List", "heading_path": ["Feature List"], "page_start": 59, "page_end": 59, "text": "Touch features"},
        ]

        sections = build_section_records(
            "doc",
            chunks,
            dropped_repeat_labels={"Feature List"},
        )

        section_ids = {s["section_id"] for s in sections}
        self.assertIn("4.2.1.1 UART", section_ids)
        self.assertNotIn("Feature List", section_ids)

    def test_build_section_records_keeps_labels_not_in_dropped_set(self):
        """Backward compat: when no dropped_repeat_labels is provided, every
        non-noisy section_id is kept (previous behavior)."""
        chunks = [
            {"chunk_id": "doc:0001", "section_id": "Feature List", "heading_path": ["Feature List"], "page_start": 10, "page_end": 10, "text": "x"},
        ]

        sections = build_section_records("doc", chunks)

        self.assertEqual([s["section_id"] for s in sections], ["Feature List"])

    def test_build_section_records_keeps_real_sections_intact(self):
        """Sanity guard for fix B: numbered sections and ordinary
        non-numbered headings (e.g. chapter titles) must NOT be dropped.
        Only the specific NOISY_TOC_HEADINGS set is filtered.
        """
        chunks = [
            {"chunk_id": "doc:0001", "section_id": "Features", "heading_path": ["Features"], "page_start": 1, "page_end": 1, "text": "Feature list"},
            {"chunk_id": "doc:0002", "section_id": "Wi-Fi", "heading_path": ["Wi-Fi"], "page_start": 2, "page_end": 2, "text": "Wi-Fi details"},
            {"chunk_id": "doc:0003", "section_id": "1 Overview", "heading_path": ["1 Overview"], "page_start": 3, "page_end": 3, "text": "Overview"},
        ]

        sections = build_section_records("doc", chunks)

        section_ids = {s["section_id"] for s in sections}
        self.assertEqual(section_ids, {"Features", "Wi-Fi", "1 Overview"})
    def test_builds_reverse_index_from_chunks_and_tables(self):
        chunks = [
            {"chunk_id": "doc:0001", "page_start": 1, "page_end": 1},
            {"chunk_id": "doc:0002", "page_start": 1, "page_end": 2},
            {"chunk_id": "doc:0003", "page_start": 3, "page_end": 3},
        ]
        tables = [
            {"table_id": "doc:table:0001", "page_start": 2, "page_end": 2},
        ]
        alerts = [
            {"kind": "empty_table_sidecar", "page": 3},
        ]

        index = build_pages_index(chunks, tables, alerts)

        self.assertEqual(len(index), 3)
        page1 = index[0]
        self.assertEqual(page1["page"], 1)
        self.assertEqual(page1["chunk_ids"], ["doc:0001", "doc:0002"])
        self.assertEqual(page1["table_ids"], [])
        self.assertEqual(page1["asset_ids"], [])

        page2 = index[1]
        self.assertEqual(page2["page"], 2)
        self.assertIn("doc:0002", page2["chunk_ids"])
        self.assertEqual(page2["table_ids"], ["doc:table:0001"])

        page3 = index[2]
        self.assertEqual(page3["page"], 3)
        self.assertEqual(page3["alert_kinds"], ["empty_table_sidecar"])

    def test_pages_index_includes_asset_ids_when_provided(self):
        assets = [
            {"asset_id": "doc:asset:0001", "page": 1},
            {"asset_id": "doc:asset:0002", "page": 2},
            {"asset_id": "doc:asset:0003", "page": 2},
        ]

        index = build_pages_index([], [], [], asset_records=assets)

        by_page = {entry["page"]: entry for entry in index}
        self.assertEqual(by_page[1]["asset_ids"], ["doc:asset:0001"])
        self.assertEqual(by_page[2]["asset_ids"], ["doc:asset:0002", "doc:asset:0003"])

    def test_empty_inputs_returns_empty(self):
        self.assertEqual(build_pages_index([], [], []), [])

    def test_skips_chunks_without_page(self):
        chunks = [{"chunk_id": "doc:0001", "page_start": None, "page_end": None}]
        self.assertEqual(build_pages_index(chunks, [], []), [])


class TocTests(unittest.TestCase):
    @staticmethod
    def _heading(text, page, label="section_header"):
        return SimpleNamespace(
            label=SimpleNamespace(value=label),
            text=text,
            prov=[SimpleNamespace(page_no=page)],
        )

    @staticmethod
    def _paragraph(text, page):
        return SimpleNamespace(
            label=SimpleNamespace(value="paragraph"),
            text=text,
            prov=[SimpleNamespace(page_no=page)],
        )

    def _doc(self, items):
        return SimpleNamespace(iterate_items=lambda: iter((item, 0) for item in items))

    def test_builds_toc_from_doc_items(self):
        heading1 = self._heading("1 Overview", 1)
        heading2 = self._heading("2.1 Pin Layout", 15)
        paragraph = self._paragraph("Some body text", 2)

        toc = build_toc(self._doc([heading1, paragraph, heading2]))

        self.assertEqual(len(toc), 2)
        self.assertEqual(toc[0]["heading"], "1 Overview")
        self.assertEqual(toc[0]["level"], 1)
        self.assertEqual(toc[0]["page"], 1)
        self.assertTrue(toc[0]["is_chapter"])
        self.assertEqual(toc[1]["heading"], "2.1 Pin Layout")
        self.assertEqual(toc[1]["level"], 2)
        self.assertEqual(toc[1]["page"], 15)
        self.assertFalse(toc[1]["is_chapter"])

    def test_empty_doc_returns_empty_toc(self):
        self.assertEqual(build_toc(SimpleNamespace()), [])

    def test_is_chapter_true_only_for_numbered_l1(self):
        items = [
            self._heading("1 Introduction", 1),
            self._heading("1.1 Scope", 2),
            self._heading("A.1 Appendix Note", 100),
            self._heading("Revision History", 120),
        ]

        toc = build_toc(self._doc(items))
        by_heading = {entry["heading"]: entry for entry in toc}

        self.assertTrue(by_heading["1 Introduction"]["is_chapter"])
        self.assertFalse(by_heading["1.1 Scope"]["is_chapter"])
        self.assertFalse(by_heading["A.1 Appendix Note"]["is_chapter"])
        self.assertFalse(by_heading["Revision History"]["is_chapter"])

    def test_drops_noisy_section_ids(self):
        items = [
            self._heading("Contents", 7),
            self._heading("List of T ables", 10),
            self._heading("List of Figures", 12),
            self._heading("Cont'd from previous page", 22),
            self._heading("1 Overview", 13),
        ]

        toc = build_toc(self._doc(items))

        self.assertEqual([e["heading"] for e in toc], ["1 Overview"])

    def test_drops_note_standalone_headings(self):
        items = [
            self._heading("Note:", 26),
            self._heading("Notes:", 44),
            self._heading("2.1 Pin Layout", 15),
        ]

        toc = build_toc(self._doc(items))

        self.assertEqual([e["heading"] for e in toc], ["2.1 Pin Layout"])

    def test_drops_table_caption_masquerading_as_heading(self):
        items = [
            self._heading("Table 2-9. Peripheral Pin Assignment", 27),
            self._heading("2.3 IO Pins", 20),
        ]

        toc = build_toc(self._doc(items))

        self.assertEqual([e["heading"] for e in toc], ["2.3 IO Pins"])

    def test_drops_bullet_prefixed_heading(self):
        # Docling's layout analyzer sometimes promotes a bullet-list entry into
        # a heading when the line's typography looks heading-like. Any heading
        # starting with a Unicode bullet glyph (·, •, ◦, ▪, ▫, ►, ◆, ∙, ⬧) is
        # structural noise — real chapter anchors never begin with a list bullet.
        items = [
            self._heading("· IO MUX:", 40),        # real datasheet case (U+00B7)
            self._heading("• System Architecture", 5),   # U+2022
            self._heading("◦ Sub-note", 10),       # U+25E6
            self._heading("▪ Item", 12),           # U+25AA
            self._heading("2.3 IO Pins", 20),      # legitimate heading kept
        ]

        toc = build_toc(self._doc(items))

        self.assertEqual([e["heading"] for e in toc], ["2.3 IO Pins"])

    def test_keeps_heading_with_non_bullet_special_chars(self):
        # Guard against over-filtering: hyphens, asterisks, and mid-text
        # middle-dots are NOT bullet prefixes and must be preserved.
        items = [
            self._heading("Wi-Fi", 3),                  # ASCII hyphen mid-text
            self._heading("2.4 GHz", 5),                # decimal + unit
            self._heading("Low-Power Modes", 67),       # hyphenated title
            self._heading("A·B Cross-reference", 8),    # middle dot mid-text
            self._heading("*Bluetooth", 72),            # ASCII asterisk (rare, but not a Unicode bullet)
        ]

        toc = build_toc(self._doc(items))

        self.assertEqual(
            [e["heading"] for e in toc],
            ["Wi-Fi", "2.4 GHz", "Low-Power Modes", "A·B Cross-reference", "*Bluetooth"],
        )

    def test_drops_repeated_unnumbered_heading(self):
        # Threshold is 3: headings repeating more than 3 times are dropped.
        # Real-world noise ("Feature List" 29x, "Pin Assignment" 15x) is
        # well above this; occasional 2-3x legitimate repeats survive.
        items = [
            self._heading("Feature List", 36),
            self._heading("Feature List", 37),
            self._heading("Feature List", 38),
            self._heading("Feature List", 39),
            self._heading("4 Functional Description", 36),
        ]

        toc = build_toc(self._doc(items))

        self.assertEqual([e["heading"] for e in toc], ["4 Functional Description"])

    def test_keeps_unnumbered_heading_with_small_repeat_count(self):
        # Two or three occurrences can be legitimate (e.g. the same short
        # non-numbered heading naturally recurring). Do not drop them.
        items = [
            self._heading("Overview", 1),
            self._heading("Overview", 50),
            self._heading("Overview", 100),
        ]

        toc = build_toc(self._doc(items))

        self.assertEqual(len(toc), 3)

    def test_keeps_repeated_numbered_heading_variants(self):
        # Numbered headings are unique anchors even if their "short name" repeats.
        items = [
            self._heading("4.2.1 GPIO", 52),
            self._heading("4.2.2 UART", 55),
            self._heading("4.2.3 SPI", 58),
        ]

        toc = build_toc(self._doc(items))

        self.assertEqual(len(toc), 3)
        self.assertTrue(all(entry["level"] == 3 for entry in toc))

    def test_keeps_unnumbered_heading_when_unique(self):
        items = [
            self._heading("Revision History", 83),
            self._heading("Disclaimer and Copyright Notice", 87),
        ]

        toc = build_toc(self._doc(items))

        self.assertEqual(len(toc), 2)

    def test_propagates_suspicious_from_section_records(self):
        items = [
            self._heading("Note:", 7),
            self._heading("Note:", 26),
            self._heading("2.1 Pin Layout", 15),
        ]
        # "Note:" survives the hardcoded drop only if we pretend it is not in
        # NOISY_TOC_HEADINGS; here we rely on the section_records cross-mark by
        # using a heading that is not in the drop list but IS suspicious.
        items = [
            self._heading("Mystery Section", 3),
            self._heading("2.1 Pin Layout", 15),
        ]
        section_records = [
            {"section_id": "Mystery Section", "suspicious": True},
            {"section_id": "2.1 Pin Layout"},
        ]

        toc = build_toc(self._doc(items), section_records=section_records)

        by_heading = {entry["heading"]: entry for entry in toc}
        self.assertTrue(by_heading["Mystery Section"].get("suspicious"))
        self.assertNotIn("suspicious", by_heading["2.1 Pin Layout"])

    def test_handles_label_without_value_attribute(self):
        # Some docling label types expose only str(); no .value
        class PlainLabel:
            def __str__(self):
                return "section_header"

        heading = SimpleNamespace(
            label=PlainLabel(),
            text="1 Overview",
            prov=[SimpleNamespace(page_no=1)],
        )

        toc = build_toc(self._doc([heading]))

        self.assertEqual(len(toc), 1)
        self.assertEqual(toc[0]["heading"], "1 Overview")


class SuspiciousSectionTests(unittest.TestCase):
    def test_flags_section_spanning_over_30_percent(self):
        sections = [
            {"section_id": "Note:", "page_start": 7, "page_end": 60},
            {"section_id": "2.1 Pin Layout", "page_start": 15, "page_end": 16},
        ]
        flag_suspicious_sections(sections, page_count=87)

        self.assertTrue(sections[0].get("suspicious"))
        self.assertIn("54/87", sections[0]["suspicious_reason"])
        self.assertNotIn("suspicious", sections[1])

    def test_does_not_flag_normal_sections(self):
        sections = [
            {"section_id": "1 Overview", "page_start": 1, "page_end": 5},
        ]
        flag_suspicious_sections(sections, page_count=100)

        self.assertNotIn("suspicious", sections[0])

    def test_no_crash_on_none_page_count(self):
        sections = [{"section_id": "X", "page_start": 1, "page_end": 50}]
        flag_suspicious_sections(sections, page_count=None)
        self.assertNotIn("suspicious", sections[0])


class HeadingOccurrenceTests(unittest.TestCase):
    @staticmethod
    def _heading(text, page, label="section_header"):
        return SimpleNamespace(
            label=SimpleNamespace(value=label),
            text=text,
            prov=[SimpleNamespace(page_no=page)],
        )

    def _doc(self, items):
        return SimpleNamespace(iterate_items=lambda: iter((item, 0) for item in items))

    def test_collect_heading_occurrences_counts_each_repeat(self):
        items = [
            self._heading("Feature List", 36),
            self._heading("Feature List", 44),
            self._heading("Feature List", 58),
            self._heading("4.1.1.1 CPU", 36),
            self._heading("Note:", 26),
        ]

        counts = collect_heading_occurrences(self._doc(items))

        self.assertEqual(counts["Feature List"], 3)
        self.assertEqual(counts["4.1.1.1 CPU"], 1)
        # Note: is filtered as a pre-noise heading and does not get counted.
        self.assertEqual(counts.get("Note:", 0), 0)

    def test_collect_heading_occurrences_handles_missing_iterate_items(self):
        counts = collect_heading_occurrences(SimpleNamespace())
        self.assertEqual(counts, {})

    def test_compute_dropped_repeat_labels_over_threshold(self):
        # Default threshold is 3; "Feature List" x4 exceeds it.
        counts = {"Feature List": 4, "4.1 Foo": 5, "Rare Label": 2}

        dropped = compute_dropped_repeat_labels(counts)

        self.assertIn("Feature List", dropped)

    def test_compute_dropped_repeat_labels_keeps_numbered_headings(self):
        # Numbered anchors must never be dropped even if their literal text
        # somehow repeats (e.g. cross-doc concatenation, rare).
        counts = {"4.2 Peripherals": 10}

        dropped = compute_dropped_repeat_labels(counts)

        self.assertNotIn("4.2 Peripherals", dropped)

    def test_compute_dropped_repeat_labels_keeps_small_repeats(self):
        # Threshold is 3; ≤ threshold keeps the heading.
        counts = {"Overview": 3, "Features": 2, "Glossary": 1}

        dropped = compute_dropped_repeat_labels(counts)

        self.assertEqual(dropped, set())


class HeadingLineageTests(unittest.TestCase):
    """Regression suite for Phase 56 heading breadcrumbs (Fix A).

    ``build_doc_item_lineages`` walks the Docling document tree in reading
    order and returns, for each item, the full ancestor heading chain. The
    chain uses ``infer_heading_level`` (numbered prefix is authoritative)
    and falls back to ``item.heading_level`` for non-numbered headings.
    Noisy headings (``Note:``, ``Table N-M.``, ``· IO MUX:``) never push
    onto the stack but still receive a snapshot so their associated chunks
    get a reasonable breadcrumb.
    """

    @staticmethod
    def _heading(text, page, level=None, label="section_header"):
        # ``level`` is Docling's own heading_level attribute (optional).
        item = SimpleNamespace(
            label=SimpleNamespace(value=label),
            text=text,
            prov=[SimpleNamespace(page_no=page)],
        )
        if level is not None:
            item.heading_level = level
        return item

    @staticmethod
    def _paragraph(text, page):
        return SimpleNamespace(
            label=SimpleNamespace(value="paragraph"),
            text=text,
            prov=[SimpleNamespace(page_no=page)],
        )

    def _doc(self, items):
        return SimpleNamespace(iterate_items=lambda: iter((item, 0) for item in items))

    def test_numbered_hierarchy_stacks_correctly(self):
        h1 = self._heading("1 Chapter A", 1)
        h2 = self._heading("1.1 Section", 2)
        h3 = self._heading("1.1.1 Subsection", 3)
        p = self._paragraph("body under subsection", 3)

        lineages = build_doc_item_lineages(self._doc([h1, h2, h3, p]))

        self.assertEqual(lineages[id(h1)], ["1 Chapter A"])
        self.assertEqual(lineages[id(h2)], ["1 Chapter A", "1.1 Section"])
        self.assertEqual(lineages[id(h3)], ["1 Chapter A", "1.1 Section", "1.1.1 Subsection"])
        self.assertEqual(
            lineages[id(p)],
            ["1 Chapter A", "1.1 Section", "1.1.1 Subsection"],
        )

    def test_sibling_numbered_heading_pops_stack(self):
        h1 = self._heading("1 A", 1)
        h2 = self._heading("1.1 B", 1)
        p1 = self._paragraph("under 1.1", 1)
        h3 = self._heading("2 D", 2)
        p2 = self._paragraph("under 2", 2)

        lineages = build_doc_item_lineages(self._doc([h1, h2, p1, h3, p2]))

        self.assertEqual(lineages[id(p1)], ["1 A", "1.1 B"])
        self.assertEqual(lineages[id(h3)], ["2 D"])
        self.assertEqual(lineages[id(p2)], ["2 D"])

    def test_noisy_heading_does_not_push_but_still_snapshots(self):
        h = self._heading("4.1.3.1 IO MUX and GPIO Matrix", 40)
        note = self._heading("Note:", 40)  # noisy
        bullet = self._heading("· IO MUX:", 40)  # noisy (bullet prefix)
        p = self._paragraph("body under noisy parent", 40)

        lineages = build_doc_item_lineages(self._doc([h, note, bullet, p]))

        # Noisy headings get the current stack without themselves being pushed
        self.assertEqual(lineages[id(note)], ["4.1.3.1 IO MUX and GPIO Matrix"])
        self.assertEqual(lineages[id(bullet)], ["4.1.3.1 IO MUX and GPIO Matrix"])
        # Subsequent non-heading items see only the real parent
        self.assertEqual(lineages[id(p)], ["4.1.3.1 IO MUX and GPIO Matrix"])

    def test_unnumbered_heading_falls_back_to_docling_heading_level(self):
        # Front-matter "Features" is level 1 per Docling (even though it
        # has no numeric prefix). Sub-items under it should stack at 2.
        features = self._heading("Features", 3, level=1)
        wifi = self._heading("Wi-Fi", 3, level=2)  # sub-bullet under Features
        p = self._paragraph("Wi-Fi details", 3)

        lineages = build_doc_item_lineages(self._doc([features, wifi, p]))

        self.assertEqual(lineages[id(features)], ["Features"])
        self.assertEqual(lineages[id(wifi)], ["Features", "Wi-Fi"])
        self.assertEqual(lineages[id(p)], ["Features", "Wi-Fi"])

    def test_unnumbered_heading_without_docling_level_defaults_to_one(self):
        h = self._heading("Revision History", 83)  # no level attr
        p = self._paragraph("v1.0 ...", 83)

        lineages = build_doc_item_lineages(self._doc([h, p]))

        self.assertEqual(lineages[id(h)], ["Revision History"])
        self.assertEqual(lineages[id(p)], ["Revision History"])

    def test_handles_missing_iterate_items(self):
        self.assertEqual(build_doc_item_lineages(SimpleNamespace()), {})

    def test_unnumbered_heading_does_not_pop_numbered_ancestors(self):
        """Regression: ``BACKUP32K_CLK`` (unnumbered bold bullet inside
        ``4.1.3.9 XTAL32K Watchdog Timers``) must not clobber numbered
        chapter ancestors. The numbered skeleton (4 / 4.1 / 4.1.3) should
        remain on the stack; the unnumbered heading nests as a child
        of the deepest numbered ancestor (level 5 under 4.1.3.9@4).
        """
        chap = self._heading("4 Functional Description", 36)
        sec1 = self._heading("4.1 System", 36)
        sec3 = self._heading("4.1.3 System Components", 40)
        subsec = self._heading("4.1.3.9 XTAL32K Watchdog Timers", 45)
        bullet = self._heading("BACKUP32K_CLK", 45)  # non-numbered, no Docling level
        p_under_bullet = self._paragraph("body under BACKUP32K_CLK", 45)
        next_numbered = self._heading("4.2 Peripherals", 51)
        p_under_next = self._paragraph("peripherals body", 51)

        lineages = build_doc_item_lineages(
            self._doc([chap, sec1, sec3, subsec, bullet, p_under_bullet, next_numbered, p_under_next])
        )

        # The bullet gets nested under 4.1.3.9, keeping 4 / 4.1 / 4.1.3 alive
        self.assertEqual(
            lineages[id(bullet)],
            ["4 Functional Description", "4.1 System", "4.1.3 System Components", "4.1.3.9 XTAL32K Watchdog Timers", "BACKUP32K_CLK"],
        )
        self.assertEqual(
            lineages[id(p_under_bullet)],
            ["4 Functional Description", "4.1 System", "4.1.3 System Components", "4.1.3.9 XTAL32K Watchdog Timers", "BACKUP32K_CLK"],
        )
        # Crucial: after popping to 4.2 level 2, the chapter "4 Functional
        # Description" is still on the stack — the unnumbered BACKUP32K_CLK
        # never pushed anything at level 1 that could have popped the chapter.
        self.assertEqual(lineages[id(next_numbered)], ["4 Functional Description", "4.2 Peripherals"])
        self.assertEqual(lineages[id(p_under_next)], ["4 Functional Description", "4.2 Peripherals"])

    def test_dropped_repeat_labels_do_not_pollute_stack(self):
        # "Feature List" repeats under many numbered parents. Without
        # filtering, it pushes as level 1 and clobbers the real chapter
        # ancestor. With dropped_repeat_labels passed in, it must be
        # skipped from the stack but still snapshot the current (sane)
        # stack for chunks directly under it.
        chap = self._heading("4 Functional Description", 36)
        sec = self._heading("4.1 System", 36)
        feature = self._heading("Feature List", 36)  # noisy recurring label
        p_under_feature = self._paragraph("bullet content", 36)
        subsec = self._heading("4.1.1 Microprocessor and Master", 36)
        p_under_subsec = self._paragraph("subsec body", 36)

        lineages = build_doc_item_lineages(
            self._doc([chap, sec, feature, p_under_feature, subsec, p_under_subsec]),
            dropped_repeat_labels={"Feature List"},
        )

        # Feature List itself and its paragraph inherit the numbered parents
        self.assertEqual(
            lineages[id(feature)],
            ["4 Functional Description", "4.1 System"],
        )
        self.assertEqual(
            lineages[id(p_under_feature)],
            ["4 Functional Description", "4.1 System"],
        )
        # Crucial regression: the numbered subsection after a dropped label
        # keeps its full ancestor chain — Feature List did not pop anything.
        self.assertEqual(
            lineages[id(subsec)],
            ["4 Functional Description", "4.1 System", "4.1.1 Microprocessor and Master"],
        )
        self.assertEqual(
            lineages[id(p_under_subsec)],
            ["4 Functional Description", "4.1 System", "4.1.1 Microprocessor and Master"],
        )

    def test_build_chunk_record_uses_item_lineage_for_heading_path(self):
        # Simulate a chunk whose first doc_item is recorded in the lineage map.
        first_item = SimpleNamespace(
            prov=[SimpleNamespace(page_no=40)],
        )
        chunk = SimpleNamespace(
            text="UART feature bullets",
            meta=SimpleNamespace(
                headings=["4.2.1.1 UART Controller"],  # chunker's single-depth view
                doc_items=[first_item],
            ),
        )
        lineages = {
            id(first_item): [
                "4 Functional Description",
                "4.2 Peripherals",
                "4.2.1 Connectivity Interface",
                "4.2.1.1 UART Controller",
            ],
        }

        record = build_chunk_record(
            doc_id="doc",
            chunk_id="doc:0001",
            chunk_index=1,
            chunk=chunk,
            contextualized_text="...",
            item_lineages=lineages,
        )

        self.assertEqual(
            record["heading_path"],
            [
                "4 Functional Description",
                "4.2 Peripherals",
                "4.2.1 Connectivity Interface",
                "4.2.1.1 UART Controller",
            ],
        )
        # section_id is the leaf (the chunker's immediate parent) —
        # preserves sections.jsonl grouping semantics.
        self.assertEqual(record["section_id"], "4.2.1.1 UART Controller")

    def test_build_chunk_record_without_lineage_preserves_chunker_headings(self):
        # Backward compat: if item_lineages is None or empty, fall back to
        # chunk.meta.headings so older call sites keep working.
        first_item = SimpleNamespace(prov=[SimpleNamespace(page_no=1)])
        chunk = SimpleNamespace(
            text="legacy",
            meta=SimpleNamespace(
                headings=["1 Overview"],
                doc_items=[first_item],
            ),
        )

        record = build_chunk_record(
            doc_id="doc",
            chunk_id="doc:0001",
            chunk_index=1,
            chunk=chunk,
            contextualized_text="1 Overview\nlegacy",
        )

        self.assertEqual(record["heading_path"], ["1 Overview"])
        self.assertEqual(record["section_id"], "1 Overview")

    def test_build_chunk_records_rejects_chunk_under_noisy_toc_section(self):
        """Regression: lineage promotion must not resurrect TOC-region chunks.

        Pre-Phase-56 the filter rejected chunks with section_id in
        ``NOISY_SECTION_IDS`` (``Contents`` / ``List of Tables`` / …).
        With lineage promotion, section_id inherits from the breadcrumb
        leaf, which may be a real section — so we now filter at
        ``build_chunk_records`` on the chunker's own attribution.
        """
        first_item = SimpleNamespace(prov=[SimpleNamespace(page_no=7)])
        toc_chunk = SimpleNamespace(
            text="1.1 Nomenclature   13\n1.2 Comparison   13\n...",
            meta=SimpleNamespace(
                headings=["Contents"],
                doc_items=[first_item],
            ),
        )
        real_chunk = SimpleNamespace(
            text="ESP32-S3 Series Comparison body",
            meta=SimpleNamespace(
                headings=["1 ESP32-S3 Series Comparison"],
                doc_items=[SimpleNamespace(prov=[SimpleNamespace(page_no=13)])],
            ),
        )

        records = build_chunk_records(
            doc_id="doc",
            chunks=[toc_chunk, real_chunk],
            contextualize=lambda c: c.text,
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["section_id"], "1 ESP32-S3 Series Comparison")
