import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.audit_geisha_source import inspect_source

class SourceAuditTest(unittest.TestCase):
    def test_identifies_modified_and_native_sensitive_scripts_without_running(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "geisha"
            (root / "js").mkdir(parents=True)
            (root / "index.html").write_text("<p>Original</p>", encoding="utf-8")
            (root / "js/environment.js").write_text(
                "wiiuEC.registerTitleDownloadTask('id', 1);"
                "wiiuNNA.getServiceToken();"
                "var text = 'Local Game Database';"
                "var url = 'https://cdn.example.org/img';",
                encoding="utf-8")
            first = (root / "js/environment.js").read_bytes()
            report = inspect_source(folder)
            self.assertEqual(report["scanned_files"], 2)
            self.assertEqual(report["counts"]["native_download"], 1)
            self.assertEqual(report["counts"]["native_account"], 1)
            self.assertEqual(report["counts"]["local_mock"], 1)
            self.assertEqual(report["counts"]["external_url"], 1)
            self.assertEqual(report["flagged"][0]["file"], "js/environment.js")
            self.assertEqual((root / "js/environment.js").read_bytes(), first)

    def test_missing_directory_is_not_silently_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                inspect_source(Path(folder) / "absent")
