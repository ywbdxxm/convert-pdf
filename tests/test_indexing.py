import unittest
from types import SimpleNamespace

from docling_batch.indexing import (
    build_chunk_record,
    build_chunk_records,
    build_section_records,
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
                "doc_id": "rm0090",
                "section_id": "Clock / PLL",
                "heading_path": ["Clock", "PLL"],
                "page_start": 10,
                "page_end": 10,
                "text": "PLL source selection",
            },
            {
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
