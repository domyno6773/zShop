import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from inspect_wps import inspect

class InspectorTest(unittest.TestCase):
    def test_original_plugin_if_available(self):
        path = ROOT / "newShop(1).wps"
        if not path.exists():
            self.skipTest("Original binary intentionally not included in public repo")
        report = inspect(path)
        self.assertEqual(report["metadata"].get("version"), "v2.2.0-safe")
        self.assertTrue(report["markers"]["eshop_applet_patch"])
        self.assertTrue(report["markers"]["remote_reporting"])
        self.assertTrue(report["markers"]["ias_auth_rewrite"])

if __name__ == "__main__":
    unittest.main()
