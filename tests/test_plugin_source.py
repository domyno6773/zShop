"""Source-level safety invariants for the zShop WUPS plugin v0.2.0."""
import re
import unittest
from pathlib import Path

SRC = (Path(__file__).resolve().parents[1] / "plugin/src/main.cpp").read_text(encoding="utf-8")

class ShopPluginTests(unittest.TestCase):
    def test_wups_metadata(self):
        self.assertIn('WUPS_PLUGIN_NAME("zShop")', SRC)
        self.assertIn('WUPS_PLUGIN_VERSION("v0.2.0-alpha")', SRC)
        self.assertIn('"vol/content/initial.oma"', SRC)

    def test_inkay_original_and_eshop_only(self):
        self.assertIn('"samurai.wup.shop.pretendo.cc"', SRC)
        self.assertIn("WUPS_FP_TARGET_PROCESS_ESHOP", SRC)
        self.assertIn("WUPS_MUST_REPLACE_FOR_PROCESS(getaddrinfo,", SRC)
        self.assertIn("WUPS_MUST_REPLACE_FOR_PROCESS(gethostbyname,", SRC)
        self.assertNotIn("WUPS_FP_TARGET_PROCESS_ALL", SRC)
        self.assertNotIn("WUPS_FP_TARGET_PROCESS_GAME_AND_MENU", SRC)

    def test_opt_in_with_no_remote_default(self):
        self.assertIn("std::atomic_bool sRouteEnabled{false}", SRC)
        self.assertIn("std::atomic<uint32_t> sLocalAddress{0}", SRC)
        self.assertIn("kRouteKey, route, false", SRC)
        self.assertIn("kAddressKey, ip, uint32_t{0}", SRC)
        self.assertIn("isPrivateNetwork(ip)", SRC)
        self.assertIn("PORT 80", SRC)

    def test_hook_delegation(self):
        self.assertIn("return real_FSOpenFile(client, block, path, mode, handle, error);", SRC)
        self.assertIn("return real_getaddrinfo(node, service, hints, result);", SRC)
        self.assertIn("return real_gethostbyname(name);", SRC)

    def test_no_content_or_credential_patch(self):
        forbidden = (
            "registerTitleDownloadTask", "ticketDownloadSync", "IdentityAuthenticationSOAP",
            "ECommerceSOAP", "NetUpdateSOAP", "ccs/download", "KernelCopyData",
            "IOSUHAX", "Mocha", "OSWriteRegister32", "WUPS_MUST_REPLACE_PHYSICAL",
            "curl_easy_", "141.148.168.106", "patchEshop(", "replace_mem",
            "FSReadFile", "memcpy(", "strcpy(", "connect(", "socket("
        )
        for term in forbidden:
            with self.subTest(term=term):
                self.assertNotIn(term, SRC)

    def test_one_host_literal_only(self):
        hosts = re.findall(r'"([a-z0-9-]+\.(?:wup\.shop\.)?pretendo\.cc)"', SRC)
        self.assertEqual(hosts, ["samurai.wup.shop.pretendo.cc"])

if __name__ == "__main__":
    unittest.main()
