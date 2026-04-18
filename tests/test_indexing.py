import unittest
from types import SimpleNamespace

from docling_bundle.indexing import (
    attach_table_references,
    build_chunk_record,
    build_chunk_records,
    build_pages_index,
    build_section_records,
    build_toc,
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
