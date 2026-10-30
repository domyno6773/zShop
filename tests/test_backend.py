import json
import sys
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend import load_catalog, make_handler

class BackendTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog(ROOT / "catalog.example.json")
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(cls.catalog))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:%d" % cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=3)
        cls.server.server_close()

    def fetch(self, path):
        with urlopen(self.base + path, timeout=3) as reply:
            return reply.read().decode("utf-8")

    def test_health(self):
        self.assertEqual(json.loads(self.fetch("/health"))["mode"], "demo")

    def test_applet_entrypoint(self):
        html = self.fetch("/ninja/wood_index.html")
        self.assertIn("My Profile", html)
        self.assertIn("lockHomeButtonMenu(false)", html)

    def test_categories_differ(self):
        best = self.fetch("/ninja/wood_index.html?view=best")
        new = self.fetch("/ninja/wood_index.html?view=new")
        mario = self.fetch("/ninja/wood_index.html?view=mario")
        self.assertIn("Best Sellers", best)
        self.assertIn("New Releases", new)
        self.assertIn("Mario Games - segnaposto", mario)
        self.assertNotIn("Puzzle di prova</strong>", mario)
        self.assertNotEqual(best, new)
        self.assertLess(best.index("Avventura di prova</strong>"),
                        best.index("Puzzle di prova</strong>"))
        self.assertLess(new.index("Corse di prova</strong>"),
                        new.index("Puzzle di prova</strong>"))

    def test_back_and_profile(self):
        html = self.fetch("/ninja/wood_index.html?view=profile")
        self.assertIn("Back to Home", html)
        self.assertIn("view=home", html)
        self.assertIn("no Nintendo or Pretendo profile data", html)

    def test_detail_never_installs(self):
        html = self.fetch("/ninja/wood_index.html?view=detail&title=demo-race")
        self.assertIn("Installation and downloads are disabled", html)
        self.assertNotIn("registerTitleDownloadTask", html)

    def test_escapes_html(self):
        html = self.fetch("/ninja/wood_index.html?view=search&q=%3Cscript%3E")
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_unknown_route(self):
        from urllib.error import HTTPError
        with self.assertRaises(HTTPError) as exception:
            self.fetch("/ias/services/IdentityAuthenticationSOAP")
        self.assertEqual(exception.exception.code, 404)

if __name__ == "__main__":
    unittest.main()
