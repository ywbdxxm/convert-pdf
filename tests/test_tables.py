import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from docling_bundle.tables import (
    ExportedTable,
    _clean_column_header,
    backfill_table_captions_from_markdown,
    classify_table_kind,
    extract_table_caption,
    build_table_manifest_records,
    export_tables,
    inject_table_sidecars_into_markdown,
    propagate_continuation_captions,
)


class TableExportTests(unittest.TestCase):
    def test_extract_table_caption_reads_plain_title_line(self):
        caption = extract_table_caption(
            "Table 5-1. Absolute Maximum Ratings\n\n| Symbol | Max |",
            "<table></table>",
        )

        self.assertEqual(caption, "Table 5-1. Absolute Maximum Ratings")

    def test_extract_table_caption_recovers_title_from_single_cell_html_table(self):
        caption = extract_table_caption(
            "| Table 2. STM32H742xI/G and STM32H743xI/G features and peripheral counts |\n|---|",
            "<table><tbody><tr><th>Table 2. STM32H742xI/G and STM32H743xI/G features and peripheral counts</th></tr></tbody></table>",
        )

        self.assertEqual(
            caption,
            "Table 2. STM32H742xI/G and STM32H743xI/G features and peripheral counts",
        )

    def test_build_table_manifest_records_includes_sidecar_paths(self):
        record = build_table_manifest_records(
            doc_id="esp32-s3-datasheet-en",
            table_index=1,
            page_start=64,
            page_end=64,
            csv_path=Path("tables/table_0001.csv"),
            label="table",
            caption="Table 5-1. Absolute Maximum Ratings",
            columns=["Parameter", "Min", "Typ", "Max", "Unit"],
        )

        self.assertEqual(record["table_id"], "esp32-s3-datasheet-en:table:0001")
        self.assertEqual(record["page_start"], 64)
        self.assertEqual(record["csv_path"], "tables/table_0001.csv")
        self.assertEqual(record["label"], "table")
        self.assertEqual(record["caption"], "Table 5-1. Absolute Maximum Ratings")
        self.assertEqual(record["kind"], "electrical")
        self.assertEqual(record["columns"], ["Parameter", "Min", "Typ", "Max", "Unit"])

    def test_build_table_manifest_records_document_index_kind(self):
        record = build_table_manifest_records(
            doc_id="esp32",
            table_index=1,
            page_start=7,
            page_end=7,
            csv_path=Path("tables/table_0001.csv"),
            label="document_index",
            caption="",
            columns=["Chapter", "Page"],
        )

        self.assertEqual(record["kind"], "document_index")
        self.assertTrue(record["is_toc"])

    def test_build_table_manifest_records_without_columns_defaults_to_generic(self):
        record = build_table_manifest_records(
            doc_id="esp32",
            table_index=1,
            page_start=1,
            page_end=1,
            csv_path=Path("tables/table_0001.csv"),
            label="table",
            caption="Something",
        )

        self.assertEqual(record["kind"], "generic")
        self.assertNotIn("columns", record)

    def test_export_tables_writes_csv_and_html(self):
        class FakeDataFrame:
            columns = ["Symbol", "Max", "Unit"]

            def to_csv(self, path, index=False):
                Path(path).write_text("a,b\n1,2\n", encoding="utf-8")

        class FakeTable:
            prov = [SimpleNamespace(page_no=64)]

            def export_to_dataframe(self, doc=None):
                return FakeDataFrame()

            def export_to_html(self, doc=None):
                return "<table><tr><th>Table 5-1. Absolute Maximum Ratings</th></tr></table>"

            def export_to_markdown(self, doc=None):
                return "Table 5-1. Absolute Maximum Ratings\n\n| Symbol | Max |"

        with tempfile.TemporaryDirectory() as tmp_dir:
            tables_dir = Path(tmp_dir) / "tables"
            records = export_tables("esp32", [FakeTable()], tables_dir)

            self.assertEqual(len(records), 1)
            self.assertTrue((tables_dir / "table_0001.csv").exists())
            self.assertEqual(records[0].record["label"], "table")
            self.assertEqual(records[0].record["caption"], "Table 5-1. Absolute Maximum Ratings")

    def test_inject_table_sidecars_into_markdown_appends_links_after_each_matched_table(self):
        markdown = (
            "## Electrical Characteristics\n\n"
            "Table 5-1. Absolute Maximum Ratings\n\n"
            "| Symbol | Min |\n"
            "|--------|-----|\n"
            "| VDD    | 3.0 |\n\n"
            "Text after table.\n"
        )
        exported_tables = [
            ExportedTable(
                record={
                    "table_id": "esp32:table:0001",
                    "page_start": 64,
                    "page_end": 64,
                    "csv_path": "tables/table_0001.csv",
                    "label": "table",
                    "caption": "Table 5-1. Absolute Maximum Ratings",
                },
                markdown=(
                    "Table 5-1. Absolute Maximum Ratings\n\n"
                    "| Symbol | Min |\n"
                    "|--------|-----|\n"
                    "| VDD    | 3.0 |"
                ),
            )
        ]

        updated = inject_table_sidecars_into_markdown(markdown, exported_tables)

        self.assertIn(
            "Table sidecar: [CSV](tables/table_0001.csv) | `esp32:table:0001`",
            updated,
        )
        self.assertLess(
            updated.index("| VDD    | 3.0 |"),
            updated.index("Table sidecar: [CSV](tables/table_0001.csv)"),
        )

    def test_inject_table_sidecars_into_markdown_appends_appendix_for_unmatched_tables(self):
        markdown = "## Pins\n\nNo inline table here.\n"
        exported_tables = [
            ExportedTable(
                record={
                    "table_id": "esp32:table:0007",
                    "page_start": 13,
                    "page_end": 13,
                    "csv_path": "tables/table_0007.csv",
                    "label": "table",
                    "caption": "Table 1-1. ESP32-S3 Series Comparison",
                },
                markdown="Table 1-1. ESP32-S3 Series Comparison\n\n| Part | Value |",
            )
        ]

        updated = inject_table_sidecars_into_markdown(markdown, exported_tables)

        self.assertIn("## Table Sidecars Appendix", updated)
        self.assertIn(
            "- p.13 `esp32:table:0007` Table 1-1. ESP32-S3 Series Comparison [CSV](tables/table_0007.csv)",
            updated,
        )

    def test_classify_table_kind_pinout(self):
        self.assertEqual(
            classify_table_kind(["Pin No.", "Pin Name", "Pin Type", "Pin Settings"]),
            "pinout",
        )
        self.assertEqual(
            classify_table_kind(["Pin No.", "GPIO 2", "IO MUX Function 1"]),
            "pinout",
        )

    def test_classify_table_kind_strap(self):
        self.assertEqual(
            classify_table_kind(["Strapping Pin", "Default Configuration", "Bit Value"]),
            "strap",
        )

    def test_classify_table_kind_electrical(self):
        self.assertEqual(
            classify_table_kind(["Parameter", "Description", "Min", "Typ", "Max", "Unit"]),
            "electrical",
        )

    def test_classify_table_kind_register(self):
        self.assertEqual(
            classify_table_kind(["Bit Field", "Field Name", "Reset Value", "Attribute"]),
            "register",
        )

    def test_classify_table_kind_revision(self):
        self.assertEqual(
            classify_table_kind(["Date", "Version", "Release Notes"]),
            "revision",
        )

    def test_classify_table_kind_timing(self):
        self.assertEqual(
            classify_table_kind(["Symbol", "Setup Time", "Hold Time", "Unit"]),
            "timing",
        )

    def test_classify_table_kind_generic_fallback(self):
        self.assertEqual(classify_table_kind(["Feature", "Value"]), "generic")
        self.assertEqual(classify_table_kind([]), "generic")

    def _make_table(self, table_id, page_start, page_end, caption, columns, label="table"):
        return ExportedTable(
            record={
                "table_id": table_id,
                "page_start": page_start,
                "page_end": page_end,
                "csv_path": f"tables/{table_id.split(':')[-1]}.csv",
                "label": label,
                "caption": caption,
                "is_toc": label == "document_index",
                "columns": columns,
            },
            markdown="",
        )

    def test_propagate_continuation_captions_inherits_from_previous(self):
        first = self._make_table("esp32:table:0008", 16, 16, "Table 2-1. Pin Overview", ["Pin No.", "Pin Name", "Pin Type"])
        second = self._make_table("esp32:table:0009", 17, 17, "", ["Pin No.", "Pin Name", "Pin Type"])

        propagate_continuation_captions([first, second])

        self.assertEqual(second.record["caption"], "Table 2-1. Pin Overview (cont'd)")
        self.assertEqual(second.record["continuation_of"], "esp32:table:0008")

    def test_propagate_continuation_captions_inherits_on_same_page(self):
        # Docling occasionally splits one logical table on one page into
        # two records. Same-page adjacency should still trigger inheritance.
        first = self._make_table("t:table:0056", 73, 73, "Table 6-9. Transmitter", ["Parameter", "Min", "Typ", "Max"])
        second = self._make_table("t:table:0057", 73, 73, "", ["Parameter", "Min", "Typ", "Max"])

        propagate_continuation_captions([first, second])

        self.assertEqual(second.record["caption"], "Table 6-9. Transmitter (cont'd)")

    def test_propagate_continuation_captions_skips_non_adjacent_pages(self):
        # Two unrelated tables on distant pages with similar column headers
        # must NOT be linked. This is the key robustness guard.
        first = self._make_table("t:table:0001", 10, 10, "Table 1-1. Comparison", ["Feature", "Variant A", "Variant B"])
        second = self._make_table("t:table:0050", 64, 64, "", ["Feature", "Variant A", "Variant B"])

        propagate_continuation_captions([first, second])

        self.assertEqual(second.record["caption"], "")
        self.assertNotIn("continuation_of", second.record)

    def test_propagate_continuation_captions_rejects_backwards_page(self):
        # A later table that appears on an earlier page is never a continuation.
        first = self._make_table("t:table:0001", 20, 20, "Table 1-1. Foo", ["A", "B", "C"])
        second = self._make_table("t:table:0002", 10, 10, "", ["A", "B", "C"])

        propagate_continuation_captions([first, second])

        self.assertEqual(second.record["caption"], "")

    def test_propagate_continuation_captions_normalizes_explicit_docling_cont_caption(self):
        first = self._make_table("t:table:0010", 18, 18, "Table 2-2. Power-Up Glitches on Pins", ["Pin", "Glitch"])
        second = self._make_table(
            "t:table:0011",
            19,
            19,
            "Table 2-2 - cont'd from previous page",
            ["Pin", "Glitch"],
        )

        propagate_continuation_captions([first, second])

        # Explicit continuation is normalised to match the column-match form
        self.assertEqual(
            second.record["caption"],
            "Table 2-2. Power-Up Glitches on Pins (cont'd)",
        )
        self.assertEqual(second.record["continuation_of"], "t:table:0010")

    def test_propagate_continuation_captions_explicit_cont_number_mismatch_keeps_original(self):
        # If Docling's cont'd caption references a different table number
        # than the previous table, we do NOT force-normalize. Safety first.
        first = self._make_table("t:table:0010", 18, 18, "Table 2-2. Power-Up Glitches", ["Pin", "Glitch"])
        second = self._make_table(
            "t:table:0011",
            19,
            19,
            "Table 5-9 - cont'd from previous page",
            ["Pin", "Glitch"],
        )

        propagate_continuation_captions([first, second])

        self.assertEqual(second.record["caption"], "Table 5-9 - cont'd from previous page")
        self.assertNotIn("continuation_of", second.record)

    def test_propagate_continuation_captions_chains_through_multiple_pages(self):
        # Table X-Y spans 3 pages; the middle captionless page must still
        # chain its continuation caption forward.
        first = self._make_table("t:table:0001", 10, 10, "Table 1-1. Foo", ["X", "Y", "Z"])
        second = self._make_table("t:table:0002", 11, 11, "", ["X", "Y", "Z"])
        third = self._make_table("t:table:0003", 12, 12, "", ["X", "Y", "Z"])

        propagate_continuation_captions([first, second, third])

        self.assertEqual(second.record["caption"], "Table 1-1. Foo (cont'd)")
        # Chained continuations stay single-suffixed — no "(cont'd) (cont'd)" stutter.
        self.assertEqual(third.record["caption"], "Table 1-1. Foo (cont'd)")

    def test_propagate_continuation_captions_does_not_overwrite_existing(self):
        first = ExportedTable(
            record={
                "table_id": "t1",
                "caption": "Table A",
                "columns": ["X", "Y", "Z"],
                "label": "table",
                "is_toc": False,
            },
            markdown="",
        )
        second = ExportedTable(
            record={
                "table_id": "t2",
                "caption": "Table B",
                "columns": ["X", "Y", "Z"],
                "label": "table",
                "is_toc": False,
            },
            markdown="",
        )
        propagate_continuation_captions([first, second])

        self.assertEqual(second.record["caption"], "Table B")
        self.assertNotIn("continuation_of", second.record)

    def test_propagate_continuation_captions_requires_column_match(self):
        first = ExportedTable(
            record={
                "table_id": "t1",
                "caption": "Table A",
                "columns": ["X", "Y", "Z"],
                "label": "table",
                "is_toc": False,
            },
            markdown="",
        )
        second = ExportedTable(
            record={
                "table_id": "t2",
                "caption": "",
                "columns": ["Entirely", "Different", "Headers"],
                "label": "table",
                "is_toc": False,
            },
            markdown="",
        )
        propagate_continuation_captions([first, second])

        self.assertEqual(second.record["caption"], "")
        self.assertNotIn("continuation_of", second.record)

    def test_propagate_continuation_captions_skips_document_index_tables(self):
        doc_idx = ExportedTable(
            record={
                "table_id": "t1",
                "caption": "",
                "columns": ["Chapter", "Page"],
                "label": "document_index",
                "is_toc": True,
            },
            markdown="",
        )
        after = ExportedTable(
            record={
                "table_id": "t2",
                "caption": "",
                "columns": ["Chapter", "Page"],
                "label": "document_index",
                "is_toc": True,
            },
            markdown="",
        )
        propagate_continuation_captions([doc_idx, after])

        self.assertEqual(after.record["caption"], "")

    def test_backfill_table_captions_from_markdown_recovers_caption_from_context(self):
        markdown = (
            "Table 4. DFSDM implementation\n\n"
            "| Feature | Value |\n"
            "|---------|-------|\n"
            "| A       | 1     |\n\n"
            "Table sidecar: [CSV](tables/table_0019.csv) | `stm32:table:0019`\n"
        )
        exported_tables = [
            ExportedTable(
                record={
                    "table_id": "stm32:table:0019",
                    "page_start": 40,
                    "page_end": 40,
                    "csv_path": "tables/table_0019.csv",
                    "label": "table",
                    "caption": "",
                },
                markdown="| Feature | Value |\n|---------|-------|",
            )
        ]

        backfill_table_captions_from_markdown(markdown, exported_tables)

        self.assertEqual(exported_tables[0].record["caption"], "Table 4. DFSDM implementation")

    def test_backfill_recovers_caption_from_revision_history_heading(self):
        markdown = (
            "## Revision History\n\n"
            "| Date | Version | Release notes |\n"
            "|------|---------|---------------|\n"
            "| 2024 | v1.0    | Initial       |\n\n"
            "Table sidecar: [CSV](tables/table_0100.csv) | `esp32:table:0100`\n"
        )
        exported_tables = [
            ExportedTable(
                record={
                    "table_id": "esp32:table:0100",
                    "page_start": 83,
                    "page_end": 83,
                    "csv_path": "tables/table_0100.csv",
                    "label": "table",
                    "caption": "",
                },
                markdown="| Date | Version | Release notes |\n|------|---------|---------------|",
            )
        ]

        backfill_table_captions_from_markdown(markdown, exported_tables)

        self.assertEqual(exported_tables[0].record["caption"], "Revision History")

    def test_clean_column_header_collapses_mirrored_labels(self):
        self.assertEqual(_clean_column_header("Pin No..Pin No."), "Pin No.")
        self.assertEqual(_clean_column_header("RTC IO Name 1.RTC IO Name 1"), "RTC IO Name 1")
        # Mirrored with whitespace tolerance
        self.assertEqual(_clean_column_header("A .A"), "A")

    def test_clean_column_header_preserves_nested_headers(self):
        # Legitimate nested header: level0="Pin Settings 6", level1="At Reset"
        self.assertEqual(_clean_column_header("Pin Settings 6.At Reset"), "Pin Settings 6.At Reset")
        self.assertEqual(_clean_column_header("IO MUX Function 1, 2, 3.F0"), "IO MUX Function 1, 2, 3.F0")
        # Data with dots should not be touched
        self.assertEqual(_clean_column_header("4.1.1.3"), "4.1.1.3")
        self.assertEqual(_clean_column_header("Ambient Temp. 3"), "Ambient Temp. 3")
        # No dot at all
        self.assertEqual(_clean_column_header("Pin No."), "Pin No.")
        self.assertEqual(_clean_column_header("Rate"), "Rate")

    def test_backfill_ignores_generic_headings(self):
        markdown = (
            "## Pin Assignment\n\n"
            "| Pin | Name |\n"
            "|-----|------|\n"
            "| 1   | VCC  |\n\n"
            "Table sidecar: [CSV](tables/table_0200.csv) | `esp32:table:0200`\n"
        )
        exported_tables = [
            ExportedTable(
                record={
                    "table_id": "esp32:table:0200",
                    "page_start": 20,
                    "page_end": 20,
                    "csv_path": "tables/table_0200.csv",
                    "label": "table",
                    "caption": "",
                },
                markdown="| Pin | Name |\n|-----|------|",
            )
        ]

        backfill_table_captions_from_markdown(markdown, exported_tables)

        # "Pin Assignment" is a generic section heading, not a table title.
        self.assertEqual(exported_tables[0].record["caption"], "")
