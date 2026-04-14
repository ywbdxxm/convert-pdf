# Docling Batch Processor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a first-version Docling batch processor that converts embedded-manual PDFs into canonical JSON, Markdown companions, and native-chunk indexes with citation-ready metadata.

**Architecture:** The processor will expose a CLI that resolves input PDFs, configures a Docling `DocumentConverter` with GPU/OCR options, exports per-document assets, and derives section/chunk indexes from native Docling chunk metadata. Index generation and filesystem layout stay in small, focused modules so tests can exercise them without running full model inference.

**Tech Stack:** Python 3.12, Docling 2.86.0, native `unittest`, JSON/JSONL, standard library CLI/filesystem/hash helpers.

---

### Task 1: Create Package Skeleton And CLI Contract

**Files:**
- Create: `docling_bundle/__init__.py`
- Create: `docling_bundle/cli.py`
- Create: `docling_bundle/config.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
import unittest

from docling_bundle.cli import build_parser


class BuildParserTests(unittest.TestCase):
    def test_parser_accepts_input_output_and_gpu_related_flags(self):
        parser = build_parser()

        args = parser.parse_args(
            [
                "convert",
                "--input",
                "manuals/raw",
                "--output",
                "manuals/processed",
                "--device",
                "cuda",
                "--ocr-engine",
                "rapidocr",
                "--tokenizer",
                "sentence-transformers/all-MiniLM-L6-v2",
            ]
        )

        self.assertEqual(args.command, "convert")
        self.assertEqual(args.input, ["manuals/raw"])
        self.assertEqual(args.output, "manuals/processed")
        self.assertEqual(args.device, "cuda")
        self.assertEqual(args.ocr_engine, "rapidocr")
        self.assertEqual(args.tokenizer, "sentence-transformers/all-MiniLM-L6-v2")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `docling/.venv/bin/python -m unittest tests.test_cli -v`
Expected: FAIL with `ModuleNotFoundError` or missing parser symbols.

- [ ] **Step 3: Write minimal implementation**

```python
# docling_bundle/cli.py
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="docling-batch")
    subparsers = parser.add_subparsers(dest="command", required=True)
    convert = subparsers.add_parser("convert")
    convert.add_argument("--input", action="append", required=True)
    convert.add_argument("--output", required=True)
    convert.add_argument("--device", default="cuda", choices=["auto", "cpu", "cuda", "mps", "xpu"])
    convert.add_argument("--ocr-engine", default="rapidocr", choices=["rapidocr", "tesseract"])
    convert.add_argument("--tokenizer", default="sentence-transformers/all-MiniLM-L6-v2")
    return parser
```

- [ ] **Step 4: Run test to verify it passes**

Run: `docling/.venv/bin/python -m unittest tests.test_cli -v`
Expected: PASS

### Task 2: Add Output Planning And Manifest Models

**Files:**
- Create: `docling_bundle/models.py`
- Create: `docling_bundle/paths.py`
- Test: `tests/test_paths.py`

- [ ] **Step 1: Write the failing test**

```python
import unittest
from pathlib import Path

from docling_bundle.paths import build_document_paths


class BuildDocumentPathsTests(unittest.TestCase):
    def test_document_paths_are_grouped_under_doc_id(self):
        paths = build_document_paths(Path("manuals/processed"), "stm32f4-rm0090")

        self.assertEqual(paths.doc_dir, Path("manuals/processed/stm32f4-rm0090"))
        self.assertEqual(paths.document_json, Path("manuals/processed/stm32f4-rm0090/document.json"))
        self.assertEqual(paths.document_markdown, Path("manuals/processed/stm32f4-rm0090/document.md"))
        self.assertEqual(paths.manifest, Path("manuals/processed/stm32f4-rm0090/manifest.json"))
        self.assertEqual(paths.sections, Path("manuals/processed/stm32f4-rm0090/sections.jsonl"))
        self.assertEqual(paths.chunks, Path("manuals/processed/stm32f4-rm0090/chunks.jsonl"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `docling/.venv/bin/python -m unittest tests.test_paths -v`
Expected: FAIL because path helpers do not exist.

- [ ] **Step 3: Write minimal implementation**

```python
# docling_bundle/paths.py
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentPaths:
    doc_dir: Path
    document_json: Path
    document_markdown: Path
    manifest: Path
    sections: Path
    chunks: Path


def build_document_paths(output_root: Path, doc_id: str) -> DocumentPaths:
    doc_dir = output_root / doc_id
    return DocumentPaths(
        doc_dir=doc_dir,
        document_json=doc_dir / "document.json",
        document_markdown=doc_dir / "document.md",
        manifest=doc_dir / "manifest.json",
        sections=doc_dir / "sections.jsonl",
        chunks=doc_dir / "chunks.jsonl",
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `docling/.venv/bin/python -m unittest tests.test_paths -v`
Expected: PASS

### Task 3: Add Section/Chunk Record Builders

**Files:**
- Create: `docling_bundle/indexing.py`
- Test: `tests/test_indexing.py`

- [ ] **Step 1: Write the failing test**

```python
import unittest
from types import SimpleNamespace

from docling_bundle.indexing import build_chunk_record, section_key_from_headings


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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `docling/.venv/bin/python -m unittest tests.test_indexing -v`
Expected: FAIL because indexing helpers are not implemented.

- [ ] **Step 3: Write minimal implementation**

```python
# docling_bundle/indexing.py
def section_key_from_headings(headings):
    if not headings:
        return "root"
    return " / ".join(headings)


def _page_numbers_for_chunk(chunk):
    pages = []
    for item in getattr(chunk.meta, "doc_items", []):
        for prov in getattr(item, "prov", []) or []:
            if getattr(prov, "page_no", None) is not None:
                pages.append(prov.page_no)
    if not pages:
        return None, None
    return min(pages), max(pages)


def build_chunk_record(doc_id, chunk_id, chunk_index, chunk, contextualized_text):
    page_start, page_end = _page_numbers_for_chunk(chunk)
    citation = f"{doc_id} p.{page_start}" if page_start == page_end else f"{doc_id} p.{page_start}-{page_end}"
    headings = list(getattr(chunk.meta, "headings", None) or [])
    return {
        "doc_id": doc_id,
        "chunk_id": chunk_id,
        "chunk_index": chunk_index,
        "section_id": section_key_from_headings(headings),
        "heading_path": headings,
        "page_start": page_start,
        "page_end": page_end,
        "text": chunk.text,
        "contextualized_text": contextualized_text,
        "doc_item_count": len(getattr(chunk.meta, "doc_items", []) or []),
        "table_like": False,
        "citation": citation,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `docling/.venv/bin/python -m unittest tests.test_indexing -v`
Expected: PASS

### Task 4: Implement Docling Configuration And Batch Execution

**Files:**
- Modify: `docling_bundle/config.py`
- Create: `docling_bundle/converter.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
import unittest

from docling_bundle.config import build_pdf_pipeline_options


class ConfigTests(unittest.TestCase):
    def test_build_pdf_pipeline_options_enables_cuda_and_rapidocr(self):
        options = build_pdf_pipeline_options(
            device="cuda",
            enable_ocr=True,
            ocr_engine="rapidocr",
            force_full_page_ocr=False,
        )

        self.assertEqual(options.accelerator_options.device.value, "cuda")
        self.assertTrue(options.do_ocr)
        self.assertEqual(options.ocr_options.backend, "torch")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `docling/.venv/bin/python -m unittest tests.test_config -v`
Expected: FAIL because configuration builder does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
# docling_bundle/config.py
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
    RapidOcrOptions,
    TesseractCliOcrOptions,
)


def build_pdf_pipeline_options(device, enable_ocr, ocr_engine, force_full_page_ocr):
    options = PdfPipelineOptions()
    options.accelerator_options = AcceleratorOptions(device=AcceleratorDevice(device))
    options.do_ocr = enable_ocr
    if ocr_engine == "rapidocr":
        options.ocr_options = RapidOcrOptions(force_full_page_ocr=force_full_page_ocr, backend="torch")
    else:
        options.ocr_options = TesseractCliOcrOptions(force_full_page_ocr=force_full_page_ocr)
    return options
```

- [ ] **Step 4: Run test to verify it passes**

Run: `docling/.venv/bin/python -m unittest tests.test_config -v`
Expected: PASS

### Task 5: Wire CLI To Export Assets And Run Summary

**Files:**
- Modify: `docling_bundle/cli.py`
- Modify: `docling_bundle/converter.py`
- Modify: `docling_bundle/indexing.py`
- Create: `tests/test_workflow.py`

- [ ] **Step 1: Write the failing test**

```python
import tempfile
import unittest
from pathlib import Path

from docling_bundle.converter import make_doc_id


class WorkflowHelpersTests(unittest.TestCase):
    def test_make_doc_id_normalizes_filename(self):
        self.assertEqual(make_doc_id(Path("STM32F4 Reference Manual.pdf")), "stm32f4-reference-manual")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `docling/.venv/bin/python -m unittest tests.test_workflow -v`
Expected: FAIL because workflow helpers do not exist.

- [ ] **Step 3: Write minimal implementation**

```python
def make_doc_id(path):
    stem = path.stem.lower()
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in stem)
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `docling/.venv/bin/python -m unittest tests.test_workflow -v`
Expected: PASS

### Task 6: Add Docs And Verification

**Files:**
- Modify: `README.md`
- Create: `docling_bundle/__main__.py`

- [ ] **Step 1: Add a runnable module entrypoint**
- [ ] **Step 2: Document CLI usage and output layout in `README.md`**
- [ ] **Step 3: Run full verification**

Run: `docling/.venv/bin/python -m unittest discover -s tests -v`
Expected: all tests pass

Run: `docling/.venv/bin/python -m docling_bundle --help`
Expected: exit 0 and CLI help output
