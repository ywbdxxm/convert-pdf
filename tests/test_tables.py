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

    def test_build_table_manifest_records_blanks_columns_for_toc_table(self):
        """Regression: TOC tables have no meaningful column schema — their
        "header row" is the first TOC entry, not a header. Emitting those
        strings as ``columns`` misleads agents that filter on column names.
        Blank them out so the field explicitly signals "no schema here".
        """
        record = build_table_manifest_records(
            doc_id="esp32",
            table_index=1,
            page_start=7,
            page_end=7,
            csv_path=Path("tables/table_0001.csv"),
            label="document_index",
            caption="",
            columns=["", "4.1.1.3", "Ultra-Low-Power Coprocessor (ULP)", "37"],
        )

        self.assertTrue(record["is_toc"])
        self.assertEqual(record["columns"], [])

    def test_build_table_manifest_records_keeps_columns_for_regular_table(self):
        # Guard against over-filtering — non-TOC tables keep their columns.
        record = build_table_manifest_records(
            doc_id="esp32",
            table_index=8,
            page_start=16,
            page_end=16,
            csv_path=Path("tables/table_0008.csv"),
            label="table",
            caption="Table 2-1. Pin Overview",
            columns=["Pin No.", "Pin Name", "Type"],
        )

        self.assertFalse(record["is_toc"])
        self.assertEqual(record["columns"], ["Pin No.", "Pin Name", "Type"])

    def test_build_table_manifest_records_includes_row_count_when_provided(self):
        """Regression: every table's ``rows`` field was ``null``. When
        Docling exposes ``TableItem.data.num_rows`` (or the caller computes
        it from the exported CSV), write that into the record so agents can
        triage tables.index.jsonl by size.
        """
        record = build_table_manifest_records(
            doc_id="esp32",
            table_index=1,
            page_start=64,
            page_end=64,
            csv_path=Path("tables/table_0001.csv"),
            label="table",
            caption="Table 5-1. Absolute Maximum Ratings",
            columns=["Parameter", "Max"],
            rows=12,
        )

        self.assertEqual(record["rows"], 12)

    def test_build_table_manifest_records_row_count_none_when_unavailable(self):
        # Docling may not expose num_rows for every table. ``rows`` stays
        # None rather than being omitted so schema shape is stable.
        record = build_table_manifest_records(
            doc_id="esp32",
            table_index=1,
            page_start=64,
            page_end=64,
            csv_path=Path("tables/table_0001.csv"),
            label="table",
            caption="x",
            columns=["A"],
        )

        self.assertIsNone(record["rows"])

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

            def to_csv(self, path, index=False, header=True):
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

    def test_export_tables_populates_row_count_from_docling_data(self):
        """Regression: Docling's ``TableItem.data.num_rows`` is the total
        grid row count (every header grid row + data rows). The
        bundle's ``rows`` field carries the *data-row* count so it
        matches what an agent counting lines in the CSV (minus the
        flattened header) would see.

        Single-header-row table with ``num_rows=5`` (1 header + 4 data)
        reports ``rows=4``.
        """
        class FakeDataFrame:
            columns = ["A", "B"]
            def to_csv(self, path, index=False, header=True):
                Path(path).write_text("A,B\n1,2\n3,4\n5,6\n7,8\n", encoding="utf-8")

        class FakeCell:
            def __init__(self, start_row_offset_idx, column_header):
                self.start_row_offset_idx = start_row_offset_idx
                self.column_header = column_header

        class FakeTable:
            prov = [SimpleNamespace(page_no=1)]
            # 1 header row (row 0) + 4 data rows (1-4)
            data = SimpleNamespace(
                num_rows=5,
                table_cells=[
                    FakeCell(0, True), FakeCell(0, True),
                    FakeCell(1, False), FakeCell(2, False),
                    FakeCell(3, False), FakeCell(4, False),
                ],
            )
            label = "table"

            def export_to_dataframe(self, doc=None):
                return FakeDataFrame()
            def export_to_html(self, doc=None):
                return "<table></table>"
            def export_to_markdown(self, doc=None):
                return "Table 1. X\n\n| A | B |"

        with tempfile.TemporaryDirectory() as tmp_dir:
            tables_dir = Path(tmp_dir) / "tables"
            records = export_tables("doc", [FakeTable()], tables_dir)
            self.assertEqual(records[0].record["rows"], 4)

    def test_export_tables_row_count_subtracts_multi_level_header(self):
        """Phase 59e: pin-map tables often have a 2-level MultiIndex
        header. Docling counts both header grid rows in ``num_rows``,
        and flattens them into a single CSV header line. Detect the
        actual number of header grid rows from ``table_cells`` and
        subtract that many, so ``rows == data_rows`` (matches
        ``wc -l CSV - 1``).
        """
        class FakeDataFrame:
            columns = ["Pin", "Type"]
            def to_csv(self, path, index=False, header=True):
                Path(path).write_text("Pin,Type\n1,IO\n2,IO\n", encoding="utf-8")

        class FakeCell:
            def __init__(self, start_row_offset_idx, column_header):
                self.start_row_offset_idx = start_row_offset_idx
                self.column_header = column_header

        class FakeTable:
            prov = [SimpleNamespace(page_no=16)]
            # 2 header rows (0, 1) + 2 data rows (2, 3); num_rows=4
            data = SimpleNamespace(
                num_rows=4,
                table_cells=[
                    FakeCell(0, True), FakeCell(0, True),
                    FakeCell(1, True), FakeCell(1, True),
                    FakeCell(2, False), FakeCell(3, False),
                ],
            )
            label = "table"

            def export_to_dataframe(self, doc=None):
                return FakeDataFrame()
            def export_to_html(self, doc=None):
                return "<table></table>"
            def export_to_markdown(self, doc=None):
                return "Table 2-1. Pinout\n\n| Pin | Type |"

        with tempfile.TemporaryDirectory() as tmp_dir:
            tables_dir = Path(tmp_dir) / "tables"
            records = export_tables("doc", [FakeTable()], tables_dir)
            # num_rows (4) - 2 header rows = 2 data rows
            self.assertEqual(records[0].record["rows"], 2)

    def test_export_tables_row_count_for_toc_table_subtracts_header(self):
        """Phase 59e: TOC tables also have a ``column_header=True`` row
        in Docling's internal model (even though P58c writes the CSV
        with ``header=False``). The subtraction from the header-row
        count happens uniformly for all tables — ``is_toc`` only
        affects whether the header is *written* to the CSV file.

        Docling's TOC table_0002 on the datasheet: num_rows=45 with
        1 column_header row, 44 data rows, CSV written with 44 lines.
        """
        class FakeDataFrame:
            columns = ["", "4.1.1.3", "Ultra-Low-Power", "37"]
            def to_csv(self, path, index=False, header=True):
                # header=False in real TOC call, so only 44 data rows written
                Path(path).write_text(",4.1.1.3,foo,37\n" * 44, encoding="utf-8")

        class FakeCell:
            def __init__(self, start_row_offset_idx, column_header):
                self.start_row_offset_idx = start_row_offset_idx
                self.column_header = column_header

        class FakeTocTable:
            prov = [SimpleNamespace(page_no=8)]
            data = SimpleNamespace(
                num_rows=45,
                table_cells=[
                    FakeCell(0, True), FakeCell(0, True),
                ] + [FakeCell(i, False) for i in range(1, 45)],
            )
            label = "document_index"

            def export_to_dataframe(self, doc=None):
                return FakeDataFrame()
            def export_to_html(self, doc=None):
                return "<table></table>"
            def export_to_markdown(self, doc=None):
                return ""

        with tempfile.TemporaryDirectory() as tmp_dir:
            tables_dir = Path(tmp_dir) / "tables"
            records = export_tables("doc", [FakeTocTable()], tables_dir)
            self.assertEqual(records[0].record["rows"], 44)

    def test_export_tables_row_count_zero_when_num_rows_is_zero(self):
        """Guard against underflow: a num_rows=0 table stays rows=0,
        not -1. (Docling never emits num_rows=0 for real tables but the
        invariant still matters.)
        """
        class FakeDataFrame:
            columns = ["A"]
            def to_csv(self, path, index=False, header=True):
                Path(path).write_text("A\n", encoding="utf-8")

        class FakeTable:
            prov = [SimpleNamespace(page_no=1)]
            data = SimpleNamespace(num_rows=0, table_cells=[])
            label = "table"

            def export_to_dataframe(self, doc=None):
                return FakeDataFrame()
            def export_to_html(self, doc=None):
                return "<table></table>"
            def export_to_markdown(self, doc=None):
                return ""

        with tempfile.TemporaryDirectory() as tmp_dir:
            tables_dir = Path(tmp_dir) / "tables"
            records = export_tables("doc", [FakeTable()], tables_dir)
            self.assertEqual(records[0].record["rows"], 0)

    def test_export_tables_row_count_falls_back_to_none_without_docling_data(self):
        """If Docling does not expose num_rows, ``rows`` stays None. We do
        NOT attempt to re-parse the CSV — keeping the code path narrow.
        """
        class FakeDataFrame:
            columns = ["A"]
            def to_csv(self, path, index=False, header=True):
                Path(path).write_text("A\n1\n", encoding="utf-8")

        class FakeTable:
            prov = [SimpleNamespace(page_no=1)]
            label = "table"
            # no .data attribute

            def export_to_dataframe(self, doc=None):
                return FakeDataFrame()
            def export_to_html(self, doc=None):
                return "<table></table>"
            def export_to_markdown(self, doc=None):
                return "Table 1. X\n\n| A |"

        with tempfile.TemporaryDirectory() as tmp_dir:
            tables_dir = Path(tmp_dir) / "tables"
            records = export_tables("doc", [FakeTable()], tables_dir)
            self.assertIsNone(records[0].record["rows"])

    def test_export_tables_omits_header_row_on_toc_csv(self):
        """Phase 58c: TOC tables (``label="document_index"``) have no
        meaningful column schema — Docling writes pandas's default
        ``['0','1','2',...]`` as the CSV first row, which is noise an
        agent accidentally opening the file would have to filter. Write
        TOC CSVs with ``header=False`` so the first row is real TOC data.

        Non-TOC tables must still write their (real) header row.
        """
        class FakeDataFrame:
            columns = ["", "4.1.1.3", "Ultra-Low-Power Coprocessor (ULP)", "37"]
            to_csv_calls: list[dict] = []

            def to_csv(self, path, index=False, header=True):
                FakeDataFrame.to_csv_calls.append({"path": str(path), "header": header})
                Path(path).write_text(",4.1.1.3,foo,37\n", encoding="utf-8")

        class FakeTocTable:
            prov = [SimpleNamespace(page_no=8)]
            label = "document_index"

            def export_to_dataframe(self, doc=None):
                return FakeDataFrame()
            def export_to_html(self, doc=None):
                return "<table></table>"
            def export_to_markdown(self, doc=None):
                return ""

        class RealDataFrame:
            columns = ["Symbol", "Max", "Unit"]

            def to_csv(self, path, index=False, header=True):
                FakeDataFrame.to_csv_calls.append({"path": str(path), "header": header})
                Path(path).write_text("Symbol,Max,Unit\n", encoding="utf-8")

        class FakeRegularTable:
            prov = [SimpleNamespace(page_no=64)]
            label = "table"

            def export_to_dataframe(self, doc=None):
                return RealDataFrame()
            def export_to_html(self, doc=None):
                return "<table><tr><th>Table 5-1. Absolute Maximum Ratings</th></tr></table>"
            def export_to_markdown(self, doc=None):
                return "Table 5-1. Absolute Maximum Ratings"

        FakeDataFrame.to_csv_calls = []
        with tempfile.TemporaryDirectory() as tmp_dir:
            tables_dir = Path(tmp_dir) / "tables"
            records = export_tables(
                "doc", [FakeTocTable(), FakeRegularTable()], tables_dir
            )

        self.assertEqual(len(records), 2)
        self.assertTrue(records[0].record["is_toc"])
        self.assertFalse(records[1].record["is_toc"])
        # to_csv was called with header=False for the TOC table
        self.assertEqual(len(FakeDataFrame.to_csv_calls), 2)
        self.assertFalse(FakeDataFrame.to_csv_calls[0]["header"])
        # Regular table keeps its header row
        self.assertTrue(FakeDataFrame.to_csv_calls[1]["header"])

    def test_export_tables_blanks_columns_for_toc_table(self):
        """Integration: the document_index label triggers is_toc=True and
        wipes the columns list — no mis-advertised schema on TOC tables.
        """
        class FakeDataFrame:
            columns = ["", "4.1.1.3", "Ultra-Low-Power Coprocessor (ULP)", "37"]
            def to_csv(self, path, index=False, header=True):
                Path(path).write_text(",4.1.1.3,foo,37\n,4.1.1.4,bar,37\n", encoding="utf-8")

        class FakeTable:
            prov = [SimpleNamespace(page_no=8)]
            label = "document_index"

            def export_to_dataframe(self, doc=None):
                return FakeDataFrame()
            def export_to_html(self, doc=None):
                return "<table></table>"
            def export_to_markdown(self, doc=None):
                return ""

        with tempfile.TemporaryDirectory() as tmp_dir:
            tables_dir = Path(tmp_dir) / "tables"
            records = export_tables("doc", [FakeTable()], tables_dir)
            self.assertTrue(records[0].record["is_toc"])
            self.assertEqual(records[0].record["columns"], [])

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

    def test_classify_table_kind_electrical_min_max_only(self):
        # Absolute maximum ratings have Min/Max but no Typ; universally seen
        # in every vendor's datasheet.
        self.assertEqual(
            classify_table_kind(["Parameter", "Description", "Min", "Max", "Unit"]),
            "electrical",
        )

    def test_classify_table_kind_electrical_with_unit_suffix_columns(self):
        # RF / audio / power tables often suffix values with units, e.g.
        # ``Min (dBm) | Typ (dBm) | Max (dBm)``. Classification must not
        # hinge on the column name being exactly "min".
        self.assertEqual(
            classify_table_kind(["Rate", "Min (dBm)", "Typ (dBm)", "Max (dBm)"]),
            "electrical",
        )

    def test_classify_table_kind_electrical_with_symbol_column(self):
        # Some datasheets use ``Symbol`` instead of ``Parameter``.
        self.assertEqual(
            classify_table_kind(["Symbol", "Min", "Max", "Unit"]),
            "electrical",
        )

    def test_classify_table_kind_electrical_with_parameter_suffix(self):
        # "Parameter 1" / "Parameter 2" variants must not defeat classification.
        self.assertEqual(
            classify_table_kind(
                ["Parameter 1", "Description", "Min", "Typ", "Max", "Unit"]
            ),
            "electrical",
        )

    def test_classify_table_kind_timing_via_time_unit_in_columns(self):
        # Tables with two of min/typ/max AND a time-unit suffix are timing.
        self.assertEqual(
            classify_table_kind(["Parameter", "Min (ns)", "Typ (ns)", "Max (ns)"]),
            "timing",
        )
        self.assertEqual(
            classify_table_kind(["Parameter", "Min (µs)", "Max (µs)"]),
            "timing",
        )

    def test_classify_table_kind_requires_two_mtm_signals(self):
        # Conservative: only one of min/typ/max → stay generic. This keeps
        # the classifier from over-reaching on stat / peak / range columns.
        self.assertEqual(
            classify_table_kind(["Parameter", "Description", "Min (µs)"]),
            "generic",
        )
        self.assertEqual(
            classify_table_kind(["Parameter", "Description", "Typ", "Unit"]),
            "generic",
        )

    def test_classify_table_kind_does_not_match_maximum_minimum_words(self):
        # Word-boundary regex must not confuse "Maximum"/"Minimum" prose
        # column titles with data columns named "Max"/"Min".
        self.assertEqual(
            classify_table_kind(["Feature", "Maximum Value", "Minimum Value"]),
            "generic",
        )
        self.assertEqual(
            classify_table_kind(["Symbol", "Typical Time Period (µs)"]),
            "generic",
        )

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

    def test_end_to_end_prefers_markdown_context_caption_over_continuation(self):
        """Regression for the caption ordering bug.

        Mirrors ESP32-S3 Table 6-9 → Table 6-10 on adjacent pages:
          - Docling extracts both tables but attaches caption only to the first.
          - Markdown between the two tables shows "Table 6-10. 125 Kbps" as the
            second table's true title.
          - Columns match, pages are adjacent — column-match continuation
            would falsely label the second table as "Table 6-9 (cont'd)".

        Expected: after export_tables + inject_table_sidecars_into_markdown
        (the real pipeline), table 2 gets "Table 6-10. 125 Kbps", NOT a
        continuation of table 1.
        """
        class FakeDataFrame:
            def __init__(self, columns, row):
                self.columns = columns
                self._row = row

            def to_csv(self, path, index=False, header=True):
                Path(path).write_text(
                    ",".join(self.columns) + "\n" + ",".join(self._row) + "\n",
                    encoding="utf-8",
                )

        class FakeTable:
            def __init__(self, page, columns, row, markdown, html):
                self.prov = [SimpleNamespace(page_no=page)]
                self.label = "table"
                self._columns = columns
                self._row = row
                self._markdown = markdown
                self._html = html

            def export_to_dataframe(self, doc=None):
                return FakeDataFrame(self._columns, self._row)

            def export_to_markdown(self, doc=None):
                return self._markdown

            def export_to_html(self, doc=None):
                return self._html

        cols = ["Parameter", "Min", "Typ", "Max", "Unit"]
        table_a_md = (
            "| Parameter | Min | Typ | Max | Unit |\n"
            "|-----------|-----|-----|-----|------|\n"
            "| A1        | 1   | 2   | 3   | dBm  |"
        )
        table_b_md = (
            "| Parameter | Min | Typ | Max | Unit |\n"
            "|-----------|-----|-----|-----|------|\n"
            "| B1        | 4   | 5   | 6   | dBm  |"
        )
        table_a = FakeTable(
            page=73,
            columns=cols,
            row=["A1", "1", "2", "3", "dBm"],
            # Docling attaches caption natively for table A
            markdown="Table 6-9. 2 Mbps\n\n" + table_a_md,
            html="<table><tr><th>Table 6-9. 2 Mbps</th></tr></table>",
        )
        table_b = FakeTable(
            page=74,
            columns=cols,
            row=["B1", "4", "5", "6", "dBm"],
            # Docling misses caption natively for table B
            markdown=table_b_md,
            html="<table></table>",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            tables_dir = Path(tmp_dir) / "tables"
            exported = export_tables("esp32", [table_a, table_b], tables_dir)

            # Pipeline-level markdown that has Table 6-10 heading before table B
            markdown = (
                "Table 6-9. 2 Mbps\n\n"
                + table_a_md + "\n\n"
                + "Table 6-10. 125 Kbps\n\n"
                + table_b_md + "\n"
            )
            inject_table_sidecars_into_markdown(markdown, exported)

        self.assertEqual(exported[0].record["caption"], "Table 6-9. 2 Mbps")
        self.assertEqual(exported[1].record["caption"], "Table 6-10. 125 Kbps")
        self.assertNotIn("continuation_of", exported[1].record)

    def test_inject_normalizes_explicit_cont_after_backfill_fills_previous(self):
        """Chained path: backfill fills the *previous* table's caption from
        markdown, then an explicit 'Table X-Y - cont'd from previous page'
        caption on the next table must number-match and normalize.

        Regression for Tables 6-10 / 6-14 on ESP32-S3 datasheet where the
        cont'd marker survived as raw text because the previous caption was
        mis-filled by the pre-backfill propagation pass.
        """
        markdown = (
            "Table 6-10. 125 Kbps\n\n"
            "| Parameter | Min | Typ | Max | Unit |\n"
            "|-----------|-----|-----|-----|------|\n"
            "| row1      | 1   | 2   | 3   | dBm  |\n\n"
            "Table sidecar: [CSV](tables/table_0057.csv) | `esp32:table:0057`\n\n"
            "<!-- page_break -->\n\n"
            "Table 6-10 - cont'd from previous page\n\n"
            "| Parameter | Min | Typ | Max | Unit |\n"
            "|-----------|-----|-----|-----|------|\n"
            "| row2      | 4   | 5   | 6   | dBm  |\n\n"
            "Table sidecar: [CSV](tables/table_0058.csv) | `esp32:table:0058`\n"
        )
        exported_tables = [
            ExportedTable(
                record={
                    "table_id": "esp32:table:0057",
                    "page_start": 73,
                    "page_end": 73,
                    "csv_path": "tables/table_0057.csv",
                    "label": "table",
                    "caption": "",  # Native extraction missed it
                    "columns": ["Parameter", "Min", "Typ", "Max", "Unit"],
                    "is_toc": False,
                },
                markdown=(
                    "| Parameter | Min | Typ | Max | Unit |\n"
                    "|-----------|-----|-----|-----|------|\n"
                    "| row1      | 1   | 2   | 3   | dBm  |"
                ),
            ),
            ExportedTable(
                record={
                    "table_id": "esp32:table:0058",
                    "page_start": 74,
                    "page_end": 74,
                    "csv_path": "tables/table_0058.csv",
                    "label": "table",
                    "caption": "Table 6-10 - cont'd from previous page",
                    "columns": ["Parameter", "Min", "Typ", "Max", "Unit"],
                    "is_toc": False,
                },
                markdown=(
                    "| Parameter | Min | Typ | Max | Unit |\n"
                    "|-----------|-----|-----|-----|------|\n"
                    "| row2      | 4   | 5   | 6   | dBm  |"
                ),
            ),
        ]

        inject_table_sidecars_into_markdown(markdown, exported_tables)

        self.assertEqual(
            exported_tables[0].record["caption"],
            "Table 6-10. 125 Kbps",
        )
        self.assertEqual(
            exported_tables[1].record["caption"],
            "Table 6-10. 125 Kbps (cont'd)",
        )
        self.assertEqual(
            exported_tables[1].record["continuation_of"],
            "esp32:table:0057",
        )

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
