import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "compat/inkay"))
from patch_skip_eshop import patch_inkay

class InkayPatchTests(unittest.TestCase):
    BASE = """void initialize() {
        patchDNS();
        patchEshop();
        patchOlvApplet();
        patchAccountSettings();
    }
"""

    def test_changes_only_eshop_call(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            source = root / "src/main.cpp"
            source.write_text(self.BASE, encoding="utf-8")
            patch_inkay(root)
            patched = source.read_text(encoding="utf-8")
            self.assertNotIn("\n        patchEshop();", patched)
            self.assertIn("\n        patchDNS();", patched)
            self.assertIn("\n        patchOlvApplet();", patched)
            self.assertIn("\n        patchAccountSettings();", patched)

    def test_refuses_unknown_structure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            source = root / "src/main.cpp"
            source.write_text("void initialize() { patchEshop(); }", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                patch_inkay(root)
            self.assertEqual(source.read_text(), "void initialize() { patchEshop(); }")

if __name__ == "__main__":
    unittest.main()
