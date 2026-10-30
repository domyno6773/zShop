"""Static guard rails for the phase-1 WUPS diagnostic source."""
import unittest
from pathlib import Path

SRC = (Path(__file__).resolve().parents[1] / "plugin/src/main.cpp").read_text(encoding="utf-8")

class DiagnosticPluginTests(unittest.TestCase):
    def test_has_valid_wups_entry_and_pass_through(self):
        self.assertIn('WUPS_PLUGIN_NAME("zShop diagnostic")', SRC)
        self.assertIn("WUPS_MUST_REPLACE(FSOpenFile,", SRC)
        self.assertIn("return real_FSOpenFile(client, block, path, mode, handle, error);", SRC)
        self.assertIn('"vol/content/initial.oma"', SRC)

    def test_diagnostics_opt_in(self):
        self.assertIn("std::atomic_bool sProbeEnabled{false}", SRC)
        self.assertIn("Enable passive eShop detection", SRC)

    def test_no_installs_network_or_memory_patches(self):
        forbidden = (
            "registerTitleDownloadTask", "ticketDownloadSync",
            "socket(", "send(", "recv(", "connect(", "HTTPClient",
            "IOSUHAX", "Mocha", "OSWriteRegister32",
            "WUPS_MUST_REPLACE_PHYSICAL", "curl_easy_",
            "141.148.168.106",
        )
        for pattern in forbidden:
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, SRC)

if __name__ == "__main__":
    unittest.main()
