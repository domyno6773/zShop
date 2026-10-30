import tempfile
import unittest
from pathlib import Path

from tools.inspect_geisha_archive import inspect


class GeishaInspectorTest(unittest.TestCase):
    def test_complete_small_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "geisha"
            folder.mkdir()
            for name in ("index.html", "always02_01.html", "shelf02_01.html"):
                (folder / name).write_text(
                    '<link rel="stylesheet" href="/geisha/css/a.css">'
                    '<script src="js/app.js"></script>', encoding="utf-8"
                )
            (folder / "css").mkdir()
            (folder / "js").mkdir()
            (folder / "css/a.css").write_text("body{}", encoding="utf-8")
            (folder / "js/app.js").write_text("// test", encoding="utf-8")
            report = inspect(tmp)
            self.assertTrue(report["reference_complete"])
            self.assertEqual(report["missing_local_resources"], [])
            self.assertEqual(len(report["html_pages"]), 3)

    def test_missing_external_and_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "index.html").write_text(
                '<script src="missing.js"></script>'
                '<img src="https://img.example.net/cover.png">'
                '<img src="../private.jpg">', encoding="utf-8"
            )
            report = inspect(tmp)
            self.assertFalse(report["reference_complete"])
            self.assertIn("missing.js", report["missing_local_resources"])
            self.assertIn("img.example.net", report["external_hosts"])
            self.assertIn("../private.jpg", report["unsafe_paths"])

    def test_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = folder / "index.html"
            source.write_text("<html></html>", encoding="utf-8")
            before = source.read_bytes()
            inspect(folder)
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual([p.name for p in folder.iterdir()], ["index.html"])
