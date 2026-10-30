"""Offline search and charts regression using synthetic Geisha DOM fixtures."""
import re
import sys
import tempfile
import threading
import unittest
from html.parser import HTMLParser
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend import make_handler
from geisha_archive import GeishaArchive
from geisha_readonly_navigation import hydrate_search, hydrate_shelf

HOME = (
    '<html><head></head><body>'
    '<div id="wrapper" class="js-top"><div id="top01_01">'
    '<ul id="el-top" class="top-main" data-isloaded="false">'
    '<li><p class="top-loading">Loading...</p></li></ul></div>'
    '<div id="sel_menu_bar"></div></div></body></html>'
)
MENU = (
    '<div id="sel_menu_bar"><ul id="ft_navi">'
    '<li id="top_link_01" class="top"><div data-href="index.html">'
    '<span>Home</span></div></li>'
    '<li id="top_link_02" class="menu"><div data-href="always01_01.html">'
    '<span>My Menu</span></div></li>'
    '</ul></div>'
)
SEARCH = (
    '<html><head><link href="css/minified/always02_01.css" rel="stylesheet">'
    '</head><body><div id="wrapper" style="display:block">'
    '<div id="header"><input name="freeword" class="textbox" maxlength="50">'
    '<a class="search-submit se" href="./always02_01.html#">'
    '<span class="search-label">Search</span></a></div>'
    '</div>' + MENU + '</body></html>'
)
SHELF = (
    '<html><head><link href="css/minified/index.css" rel="stylesheet">'
    '</head><body><div id="wrapper" class="js-top" style="display:none">'
    '<div id="top01_01">Boot</div></div>'
    '<div id="wrapper" class="js-shelf" style="display:block">'
    '<div id="el-header"><div class="search-headline"><h1>Charts</h1>'
    '<span class="total-results">Results: 83</span></div></div>'
    '<div class="pagenation"><ul><li>1</li></ul></div>'
    '<ul id="shelf-list" class="shelf-list-item" data-isloaded="false">'
    '<p class="loading">Loading...</p></ul></div>'
    + MENU + '</body></html>'
)
CATALOG = [
    dict(name="Corsa Zero", id="demo-race", category="race",
         description="Gioco di corse", release="2026-10-01", popularity=15),
    dict(name="Puzzle Aurora", id="demo-puzzle", category="puzzle",
         description="Enigma", release="2026-10-20", popularity=5),
]


class FormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms = []
        self.buttons = []
        self.inputs = []
    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "form":
            self.forms.append(data)
        elif tag == "button":
            self.buttons.append(data)
        elif tag == "input":
            self.inputs.append(data)


class ReadOnlyNavigationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name) / "geisha"
        root.mkdir()
        for path, source in (("index.html", HOME),
                             ("always02_01.html", SEARCH),
                             ("shelf02_01.html", SHELF)):
            (root / path).write_text(source, encoding="utf-8")
        self.archive = GeishaArchive(self.tmp.name, CATALOG)

    def test_historical_search_form_is_native_without_original_js(self):
        mime, data = self.archive.read("/geisha/always02_01.html")
        page = data.decode("utf-8")
        parser = FormParser()
        parser.feed(page)
        self.assertEqual(mime, "text/html; charset=utf-8")
        self.assertEqual(len(parser.forms), 1)
        self.assertEqual(parser.forms[0]["action"], "shelf02_01.html")
        self.assertEqual(parser.forms[0]["method"], "get")
        self.assertEqual(parser.inputs[0]["name"], "freeword")
        self.assertEqual(parser.buttons[0]["type"], "submit")
        self.assertEqual(parser.buttons[0]["class"], "search-submit se")
        self.assertIn("search-label", page)
        self.assertIn("ft_navi", page)
        self.assertIn('href="index.html"', page)
        self.assertNotIn('href="always01_01.html"', page)
        self.assertEqual(page.count("zshop-bridge.js"), 1)

    def test_historical_shelf_classes_and_search(self):
        _, data = self.archive.read("/geisha/shelf02_01.html", query="corsa")
        page = data.decode("utf-8")
        self.assertIn("Search Results", page)
        self.assertIn('id="shelf-list"', page)
        self.assertIn('class="m-list-item"', page)
        self.assertIn('class="list-title-outline"', page)
        self.assertIn('class="list-title-icon"', page)
        self.assertIn('class="list-title-summary"', page)
        self.assertIn("Corsa Zero", page)
        self.assertNotIn("Puzzle Aurora", page)
        self.assertIn("Results: 1", page)
        self.assertIn('data-isloaded="true"', page)
        self.assertNotIn('class="loading"', page)
        self.assertNotIn('href="money01_01.html"', page)
        self.assertIn('#wrapper.js-top{display:none!important}', page)
        self.assertIn('#wrapper.js-shelf{display:block!important}', page)
        self.assertIn('id="ft_navi"', page)
        self.assertNotIn('class="pagenation"', page)
        self.assertIn('id="el-sort"', page) if 'id="el-sort"' in SHELF else None

    def test_charts_show_sorted_catalog_without_fake_archive_counts(self):
        _, data = self.archive.read("/geisha/shelf02_01.html")
        page = data.decode("utf-8")
        self.assertLess(page.index("Corsa Zero"), page.index("Puzzle Aurora"))
        self.assertIn("Results: 2", page)
        self.assertNotIn("Results: 83", page)

    def test_empty_result_is_not_loading(self):
        _, data = self.archive.read("/geisha/shelf02_01.html", query="impossibile")
        page = data.decode("utf-8")
        self.assertIn("Nessun risultato", page)
        self.assertIn("Results: 0", page)
        self.assertNotIn("Loading...", page)

    def test_escaped_catalog_fields_and_no_active_commerce(self):
        malicious = dict(CATALOG[0], name='<img src=x onerror=alert(1)>')
        page = hydrate_shelf(SHELF, [malicious], query="")
        self.assertIn("&lt;img", page)
        self.assertNotIn("<img src=x", page)
        for forbidden in ("registerTitleDownloadTask", "ticketDownloadSync",
                          "wiiuEC.", "wiiuNNA.", "href=\"always01_01.html\""):
            self.assertNotIn(forbidden, page)

    def test_archive_sources_not_modified(self):
        original = (Path(self.tmp.name) / "geisha/always02_01.html").read_bytes()
        self.archive.read("/geisha/always02_01.html")
        self.archive.read("/geisha/shelf02_01.html", query="corsa")
        self.assertEqual(
            (Path(self.tmp.name) / "geisha/always02_01.html").read_bytes(),
            original
        )

    def test_unknown_archive_pages_preserved(self):
        self.assertEqual(hydrate_search("<div>Something else</div>"),
                         "<div>Something else</div>")
        self.assertEqual(hydrate_shelf("<div>Something else</div>", CATALOG),
                         "<div>Something else</div>")

    def test_real_http_uses_query_and_only_safe_bridge(self):
        server = ThreadingHTTPServer(
            ("127.0.0.1", 0), make_handler(CATALOG, geisha=self.archive)
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = "http://127.0.0.1:%d" % server.server_address[1]
            with urlopen(base + "/geisha/shelf02_01.html?freeword=Corsa",
                         timeout=3) as response:
                data = response.read().decode("utf-8")
                self.assertIn("Corsa Zero", data)
                self.assertNotIn("Puzzle Aurora", data)
                self.assertEqual(data.count("<script"), 1)
                self.assertIn('src="/geisha/zshop-bridge.js"', data)
            with urlopen(base + "/geisha/always02_01.html", timeout=3) as response:
                search_page = response.read().decode("utf-8")
                self.assertIn('method="get" action="shelf02_01.html"', search_page)
                self.assertIn("form-action 'self'",
                              response.headers["Content-Security-Policy"])
            with urlopen(base + "/geisha/index.html", timeout=3) as response:
                self.assertIn("form-action 'none'",
                              response.headers["Content-Security-Policy"])
        finally:
            server.shutdown()
            thread.join(timeout=3)
            server.server_close()


if __name__ == "__main__":
    unittest.main()
