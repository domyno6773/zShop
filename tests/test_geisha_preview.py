"""Regression and safety checks for local historical Geisha preview."""
import sys
import json
import tempfile
import threading
import unittest
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from geisha_archive import GeishaArchive
from backend import load_catalog, make_handler


class GeishaPreviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.bundle = Path(self.tmp.name) / "geisha"
        self.bundle.mkdir()
        (self.bundle / "index.html").write_text(
            '<!doctype html><html><head><link rel="stylesheet" href="css/main.css">'
            '<script src="js/minified/boot.js"></script></head>'
            '<body onload="bad()"><h1>Historic eShop shell</h1>'
            '<form action="https://remote.invalid/session"><input value="x"></form>'
            '<a href="javascript:bad()">action</a>'
            '<iframe src="https://remote.invalid/embed"></iframe>'
            '</body></html>', encoding="utf-8"
        )
        (self.bundle / "css").mkdir()
        (self.bundle / "css/main.css").write_text(
            "h1{color:red;background:url('https://remote.invalid/pic')}"
            "@import url(https://remote.invalid/x.css);", encoding="utf-8"
        )
        (self.bundle / "js").mkdir()
        (self.bundle / "js/minified").mkdir()
        (self.bundle / "js/minified/boot.js").write_text(
            "wiiuEC.ticketDownloadSync('never');", encoding="utf-8"
        )
        (self.bundle / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        self.archive = GeishaArchive(self.tmp.name)

    def test_original_layout_retained_while_scripts_removed(self):
        mime, page = self.archive.read("/geisha/index.html")
        text = page.decode("utf-8")
        self.assertIn("text/html", mime)
        self.assertIn("Historic eShop shell", text)
        self.assertIn("/geisha/zshop-bridge.js", text)
        self.assertEqual(text.count("<script"), 1)
        self.assertNotIn("js/minified/boot.js", text)
        self.assertIn('href="css/main.css"', text)
        self.assertIn('name="zshop-geisha-mode"', text)
        for blocked in ("onload=", "<iframe", "<form",
                        "javascript:", "https://remote.invalid"):
            with self.subTest(blocked=blocked):
                self.assertNotIn(blocked, text)

    def test_js_and_traversals_denied(self):
        forbidden = [
            "/geisha/js/minified/boot.js",
            "/geisha/%2e%2e/secret.txt",
            "/geisha/%2fetc/passwd",
            "/geisha/../index.html",
            "/geisha/.env",
            "/geisha/missing.css",
            "/ninja/ws/my/session/!open",
        ]
        for item in forbidden:
            with self.subTest(item=item):
                self.assertIsNone(self.archive.read(item))

    def test_sanitizes_external_css(self):
        mime, data = self.archive.read("/geisha/css/main.css")
        self.assertEqual(mime, "text/css; charset=utf-8")
        self.assertNotIn("remote.invalid", data.decode("utf-8"))

    def test_image_is_untouched_and_source_is_read_only(self):
        path = self.bundle / "index.html"
        before = path.read_bytes()
        self.assertEqual(self.archive.read("/geisha/image.png")[1], b"\x89PNG\r\n\x1a\n")
        self.archive.read("/geisha/index.html")
        self.assertEqual(path.read_bytes(), before)

    def test_invalid_archive_rejected(self):
        with self.assertRaises(ValueError):
            GeishaArchive(Path(self.tmp.name) / "does-not-exist")


class GeishaHttpIntegrationTests(GeishaPreviewTests):
    def setUp(self):
        super().setUp()
        catalog = load_catalog(ROOT / "catalog.example.json")
        self.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), make_handler(catalog, geisha=self.archive)
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = "http://127.0.0.1:%d" % self.server.server_address[1]
        self.addCleanup(self.stop_server)

    def stop_server(self):
        self.server.shutdown()
        self.thread.join(timeout=3)
        self.server.server_close()

    def test_applet_redirect_and_preview(self):
        with urlopen(self.base + "/ninja/wood_index.html?version=1.0.0", timeout=3) as response:
            self.assertTrue(response.geturl().endswith("/geisha/index.html"))
            self.assertIn("Historic eShop shell", response.read().decode("utf-8"))
            self.assertIn("script-src 'self'", response.headers["Content-Security-Policy"])

    def test_original_image_and_css_available(self):
        for path in ("/geisha/image.png", "/geisha/css/main.css"):
            with urlopen(self.base + path, timeout=3) as response:
                self.assertEqual(response.status, 200)

    def test_no_unsafe_api_or_js(self):
        for path in ("/geisha/js/minified/boot.js", "/ias/services/IdentityAuthenticationSOAP",
                     "/ninja/ws/my/session/!open", "/geisha/../README.md"):
            with self.subTest(path=path), self.assertRaises(HTTPError) as error:
                urlopen(self.base + path, timeout=3)
            self.assertEqual(error.exception.code, 404)

    def test_health_still_available(self):
        with urlopen(self.base + "/health", timeout=3) as response:
            health = json.loads(response.read())
            self.assertEqual(health['status'], 'ok')
            self.assertEqual(health['mode'], 'geisha-preview')


if __name__ == "__main__":
    unittest.main()
