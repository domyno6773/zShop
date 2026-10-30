"""Wii U storefront integration and navigation regression checks."""
import sys
import threading
import unittest
from html.parser import HTMLParser
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend import load_catalog, make_handler
from shop_ui import link, VIEWS

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.stylesheets = []
        self.scripts = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "a":
            self.hrefs.append(data.get("href", ""))
        if tag == "link":
            self.stylesheets.append(data.get("href", ""))
        if tag == "script":
            self.scripts.append(data.get("src", ""))
        if data.get("id"):
            self.ids.append(data["id"])


class ShopUiTests(unittest.TestCase):
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

    def request(self, path):
        with urlopen(self.base + path, timeout=3) as response:
            return response.status, response.headers, response.read().decode("utf-8")

    def page(self, view="home", **params):
        return self.request(link(view, **params))[2]

    def test_masthead_and_sidebar(self):
        home = self.page()
        self.assertIn('class="side-menu"', home)
        self.assertIn('class="top-tabs"', home)
        self.assertIn("zShop", home)
        self.assertIn("Il mio menu", home)
        self.assertIn("Indietro", home)
        self.assertIn("/static/shop.js", home)
        self.assertIn("/static/shop.css", home)
        self.assertNotIn("registerTitleDownloadTask", home)

    def test_all_views_return_usable_html(self):
        for view in VIEWS:
            with self.subTest(view=view):
                result = self.page(view)
                self.assertIn('<html lang="it">', result)
                self.assertIn('id="back-button"', result)
                self.assertIn('href="/ninja/wood_index.html?view=home"', result)
                self.assertIn("</html>", result)

    def test_categories_have_distinct_results(self):
        best = self.page("best")
        new = self.page("new")
        mario = self.page("mario")
        self.assertIn("Classifiche", best)
        self.assertIn("Ultime uscite", new)
        self.assertIn("Mario Games - segnaposto", mario)
        self.assertNotIn("Puzzle di prova</strong>", mario)
        self.assertLess(best.index("Avventura di prova</strong>"),
                        best.index("Puzzle di prova</strong>"))
        self.assertLess(new.index("Corse di prova</strong>"),
                        new.index("Puzzle di prova</strong>"))

    def test_real_navigation_links_no_dead_end(self):
        for view in ("home", "best", "new", "mario", "all", "profile"):
            parser = Links()
            parser.feed(self.page(view))
            self.assertIn("/ninja/wood_index.html?view=home", parser.hrefs)
            self.assertIn("/ninja/wood_index.html?view=profile", parser.hrefs)
            self.assertIn("/ninja/wood_index.html?view=search", parser.hrefs)
            self.assertIn("back-button", parser.ids)
            for destination in parser.hrefs:
                self.assertTrue(destination.startswith("/ninja/wood_index.html?view="))
                self.request(destination)

    def test_detail_keeps_parent_view(self):
        details = self.page("detail", title="demo-race", frm="new")
        self.assertIn('href="/ninja/wood_index.html?view=new"', details)
        self.assertIn("Corse di prova", details)
        self.assertIn("Installation and downloads are disabled", details)
        self.assertNotIn("registerTitleDownloadTask", details)

    def test_search_escaping(self):
        text = self.page("search", q='<script>alert("x")</script>')
        self.assertNotIn('<script>alert("x")</script>', text)
        self.assertIn("&lt;script&gt;", text)
        self.assertIn("0 risultati", text)

    def test_assets_served_with_mime_types(self):
        status, headers, css = self.request("/static/shop.css")
        self.assertEqual(status, 200)
        self.assertIn("text/css", headers["Content-Type"])
        self.assertIn(".side-menu", css)
        status, headers, js = self.request("/static/shop.js")
        self.assertEqual(status, 200)
        self.assertIn("javascript", headers["Content-Type"])
        self.assertIn("endStartUp(true)", js)
        self.assertIn("lockHomeButtonMenu(false)", js)

    def test_js_old_engine_baseline(self):
        js = self.request("/static/shop.js")[2]
        for forbidden in ("const ", "let ", "=>", "async ", "fetch(", "import "):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, js)

    def test_no_external_resources(self):
        page = self.page()
        parser = Links()
        parser.feed(page)
        self.assertEqual(parser.stylesheets, ["/static/shop.css"])
        self.assertEqual(parser.scripts, ["/static/shop.js"])
        self.assertNotIn('src="http', page)

    def test_no_credential_or_commerce_routes(self):
        for path in ("/ias/services/IdentityAuthenticationSOAP",
                     "/ecs/services/ECommerceSOAP",
                     "/ccs/download/0000",
                     "/static/unexpected.js"):
            with self.subTest(path=path):
                with self.assertRaises(HTTPError) as e:
                    self.request(path)
                self.assertEqual(e.exception.code, 404)

    def test_profile_explicitly_demo_only(self):
        page = self.page("profile")
        self.assertIn("Profilo non collegato", page)
        self.assertIn("no Nintendo or Pretendo profile data", page)

    def test_unknown_title_does_not_crash(self):
        self.assertIn("Gioco non trovato", self.page("detail", title="invalid"))

if __name__ == "__main__":
    unittest.main()
