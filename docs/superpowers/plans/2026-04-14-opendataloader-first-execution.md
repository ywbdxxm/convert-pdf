# OpenDataLoader-First Execution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and run an independent `OpenDataLoader PDF hybrid` pipeline first, package its output into a Codex-facing bundle under `manuals/processed/opendataloader_hybrid/`, then use what we learned to scope `docling_bundle` optimization and decide whether `docling_bundle` should be renamed.

**Architecture:** Keep tool bundles independent. Create a dedicated OpenDataLoader workspace and runner scripts, add a thin Python bundler that turns OpenDataLoader outputs into a Codex-facing folder without forcing Docling semantics, then inspect the real output before touching `docling_bundle`.

**Tech Stack:** Python 3.12, shell scripts, Java 11+, `opendataloader-pdf[hybrid]`, `unittest`

---

### Task 1: OpenDataLoader Workspace And Runner

**Files:**
- Create: `opendataloader/README.md`
- Create: `opendataloader/requirements.txt`
- Create: `scripts/bootstrap_opendataloader_env.sh`
- Create: `scripts/run_opendataloader_hybrid.sh`

- [ ] **Step 1: Write the failing test for runner assumptions**

```python
import unittest
from pathlib import Path


class OpenDataLoaderLayoutTests(unittest.TestCase):
    def test_runner_files_exist(self):
        self.assertTrue(Path("scripts/bootstrap_opendataloader_env.sh").exists())
        self.assertTrue(Path("scripts/run_opendataloader_hybrid.sh").exists())
        self.assertTrue(Path("opendataloader/README.md").exists())
        self.assertTrue(Path("opendataloader/requirements.txt").exists())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_opendataloader_layout.OpenDataLoaderLayoutTests.test_runner_files_exist -v`
Expected: `FAIL` because the files do not exist yet.

- [ ] **Step 3: Write minimal implementation**

```text
opendataloader/README.md:
- purpose of the OpenDataLoader overlay
- Java requirement
- bootstrap command
- hybrid server command
- conversion command

opendataloader/requirements.txt:
opendataloader-pdf[hybrid]

scripts/bootstrap_opendataloader_env.sh:
- create `opendataloader/.venv`
- install `opendataloader/requirements.txt`
- print Java and CLI versions

scripts/run_opendataloader_hybrid.sh:
- accept input PDF/folder and output directory
- start from `opendataloader/.venv`
- run `opendataloader-pdf` with `--hybrid docling-fast`
- request `markdown,json,html`
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_opendataloader_layout.OpenDataLoaderLayoutTests.test_runner_files_exist -v`
Expected: `OK`

- [ ] **Step 5: Verify runner help output**

Run: `bash scripts/run_opendataloader_hybrid.sh --help`
Expected: usage text with required input/output arguments.

### Task 2: OpenDataLoader Bundle Builder

**Files:**
- Create: `opendataloader_hybrid/__init__.py`
- Create: `opendataloader_hybrid/paths.py`
- Create: `opendataloader_hybrid/bundle.py`
- Create: `opendataloader_hybrid/cli.py`
- Test: `tests/test_opendataloader_bundle.py`

- [ ] **Step 1: Write the failing tests**

```python
import json
import tempfile
import unittest
from pathlib import Path

from opendataloader_hybrid.bundle import build_bundle


class OpenDataLoaderBundleTests(unittest.TestCase):
    def test_build_bundle_creates_entry_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native_dir = root / "native"
            native_dir.mkdir()
            (native_dir / "document.json").write_text(json.dumps({"kids": []}), encoding="utf-8")
            (native_dir / "document.md").write_text("# Title\n", encoding="utf-8")
            (native_dir / "document.html").write_text("<h1>Title</h1>", encoding="utf-8")

            out_dir = root / "bundle"
            build_bundle(
                doc_id="sample-doc",
                source_pdf_path="manuals/raw/example.pdf",
                native_dir=native_dir,
                out_dir=out_dir,
            )

            self.assertTrue((out_dir / "README.generated.md").exists())
            self.assertTrue((out_dir / "manifest.json").exists())
            self.assertTrue((out_dir / "quality-summary.md").exists())

    def test_build_bundle_creates_pages_and_element_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native_dir = root / "native"
            native_dir.mkdir()
            (native_dir / "document.json").write_text(
                json.dumps(
                    {
                        "kids": [
                            {
                                "type": "paragraph",
                                "page": 2,
                                "bbox": [0, 0, 10, 10],
                                "text": "hello",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (native_dir / "document.md").write_text("hello\n", encoding="utf-8")
            (native_dir / "document.html").write_text("<p>hello</p>", encoding="utf-8")

            out_dir = root / "bundle"
            build_bundle(
                doc_id="sample-doc",
                source_pdf_path="manuals/raw/example.pdf",
                native_dir=native_dir,
                out_dir=out_dir,
            )

            self.assertTrue((out_dir / "elements.index.jsonl").exists())
            self.assertTrue((out_dir / "pages" / "page_0002.md").exists())
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m unittest tests.test_opendataloader_bundle -v`
Expected: `ImportError` or `FAIL` because the package does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```text
opendataloader_hybrid/paths.py:
- define bundle paths for `document.*`, `pages/`, `tables/`, `figures/`, `runtime/`

opendataloader_hybrid/bundle.py:
- load OpenDataLoader `document.json`
- copy or normalize `document.json`, `document.md`, `document.html`
- write `manifest.json`
- flatten page/bbox/text records into `elements.index.jsonl`
- create `pages/page_XXXX.md`
- write `README.generated.md`
- write `quality-summary.md`
- emit `alerts.json` when key expected files/fields are missing

opendataloader_hybrid/cli.py:
- parse `--doc-id`, `--source-pdf`, `--native-dir`, `--output-dir`
- call `build_bundle(...)`
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m unittest tests.test_opendataloader_bundle -v`
Expected: `OK`

- [ ] **Step 5: Verify CLI round-trip**

Run: `python -m opendataloader_hybrid.cli --help`
Expected: usage text with required bundle arguments.

### Task 3: Run OpenDataLoader Hybrid On Real Manuals

**Files:**
- Modify: `scripts/run_opendataloader_hybrid.sh`
- Create: `manuals/processed/opendataloader_hybrid/.gitkeep`
- Modify: `findings.md`
- Modify: `progress.md`
- Modify: `task_plan.md`

- [ ] **Step 1: Write the failing smoke test**

```python
import unittest
from pathlib import Path


class OpenDataLoaderOutputSmokeTests(unittest.TestCase):
    def test_processed_root_exists(self):
        self.assertTrue(Path("manuals/processed/opendataloader_hybrid").exists())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_opendataloader_layout.OpenDataLoaderOutputSmokeTests.test_processed_root_exists -v`
Expected: `FAIL` because the output root is not present yet.

- [ ] **Step 3: Run the real pipeline**

```bash
bash scripts/bootstrap_opendataloader_env.sh
bash scripts/run_opendataloader_hybrid.sh \
  --input manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf \
  --output manuals/processed/opendataloader_hybrid-native
python -m opendataloader_hybrid.cli \
  --doc-id esp32-s3-datasheet-en \
  --source-pdf manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf \
  --native-dir manuals/processed/opendataloader_hybrid-native/esp32-s3-datasheet-en \
  --output-dir manuals/processed/opendataloader_hybrid/esp32-s3-datasheet-en
```

- [ ] **Step 4: Run smoke test to verify it passes**

Run: `python -m unittest tests.test_opendataloader_layout.OpenDataLoaderOutputSmokeTests.test_processed_root_exists -v`
Expected: `OK`

- [ ] **Step 5: Record findings**

```text
- note install/runtime constraints
- note actual native output filenames
- note whether page/bbox/table/image metadata survived
- note first-pass Codex usability
```

### Task 4: Rename Assessment And Docling Follow-Up

**Files:**
- Modify: `findings.md`
- Modify: `progress.md`
- Modify: `task_plan.md`
- Modify: `docs/superpowers/specs/2026-04-14-independent-tool-output-design.md`

- [ ] **Step 1: Write the assessment question**

```text
Does the current name `docling_bundle` still describe the code after OpenDataLoader is added and after Docling responsibilities are reduced to a Codex-facing bundle builder?
```

- [ ] **Step 2: Inspect code and responsibilities**

Run: `rg -n "docling_bundle" docling_bundle tests docs README.md AGENTS.md`
Expected: an inventory of package, doc, and command references.

- [ ] **Step 3: Record a decision, not a rename yet**

```text
Possible decisions:
- keep the name for backwards compatibility during comparison
- rename after comparison when the final Docling bundle shape is stable
- rename immediately only if the current name becomes actively misleading
```

- [ ] **Step 4: Update the implementation queue**

Run: `sed -n '1,240p' task_plan.md`
Expected: a next phase that starts `docling_bundle` optimization only after OpenDataLoader output inspection.
