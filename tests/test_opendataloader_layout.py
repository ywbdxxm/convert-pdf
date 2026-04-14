import unittest
from pathlib import Path


class OpenDataLoaderLayoutTests(unittest.TestCase):
    def test_runner_files_exist(self):
        self.assertTrue(Path("scripts/bootstrap_opendataloader_env.sh").exists())
        self.assertTrue(Path("scripts/run_opendataloader_hybrid.sh").exists())
        self.assertTrue(Path("opendataloader/README.md").exists())
        self.assertTrue(Path("opendataloader/requirements.txt").exists())

    def test_bootstrap_reuses_shared_ai_base(self):
        script = Path("scripts/bootstrap_opendataloader_env.sh").read_text(encoding="utf-8")
        self.assertIn("--system-site-packages", script)
        self.assertIn("MICROMAMBA_BIN", script)
        self.assertIn("AI_BASE_ENV_NAME", script)

    def test_runner_uses_output_dir_flag(self):
        script = Path("scripts/run_opendataloader_hybrid.sh").read_text(encoding="utf-8")
        self.assertIn("--output-dir", script)

    def test_runner_enables_hybrid_fallback(self):
        script = Path("scripts/run_opendataloader_hybrid.sh").read_text(encoding="utf-8")
        self.assertIn("--hybrid-fallback", script)

    def test_runner_writes_run_log(self):
        script = Path("scripts/run_opendataloader_hybrid.sh").read_text(encoding="utf-8")
        self.assertIn("run.log", script)


class OpenDataLoaderOutputSmokeTests(unittest.TestCase):
    def test_processed_root_exists(self):
        self.assertTrue(Path("manuals/processed/opendataloader_hybrid").exists())
