"""The archived Geisha Home must not remain forever on 'Loading...'."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from geisha_archive import GeishaArchive
from geisha_preview_renderer import hydrate_index

ARCHIVED_HOME = (
    '<!doctype html><html><head><link rel="stylesheet"'
    ' href="css/minified/index.css"></head><body>'
    '<div id="wrapper" class="js-top"><div id="top01_01">'
    '<ul class="top-header"><li><a href="shelf02_01.html">Charts</a></li></ul>'
    '<ul id="el-top" class="top-main" data-isloaded="false">'
    '<li><p class="top-loading">Loading...</p></li></ul>'
    '</div><div id="sel_menu_bar"></div></div>'
    '<script src="js/minified/boot.js"></script></body></html>'
)


class GeishaHomeHydrationTest(unittest.TestCase):
    def test_archive_structure_hydrated_with_historical_classes(self):
        with tempfile.TemporaryDirectory() as temp:
            geisha = Path(temp) / "geisha"
            geisha.mkdir()
            (geisha / "index.html").write_text(ARCHIVED_HOME, encoding="utf-8")
            archive = GeishaArchive(temp, [
                {"id": "test", "name": 'Demo <script>x</script>', "popularity": 3},
                {"id": "less", "name": "Second demo", "popularity": 1},
            ])
            mime, html = archive.read("/geisha/index.html")
            page = html.decode("utf-8")
            self.assertEqual(mime, "text/html; charset=utf-8")
            self.assertIn('class="top-header"', page)
            self.assertIn('id="zshop-geisha-visibility"', page)
            self.assertIn("#wrapper{display:block!important}", page)
            self.assertIn('class="top-main" data-isloaded="true"', page)
            self.assertIn('class="top-content"', page)
            self.assertIn('class="top-content-img lazy"', page)
            self.assertIn('id="ft_navi"', page)
            self.assertIn("top_link_04", page)
            self.assertIn("always02_01.html", page)
            self.assertNotIn("Loading...", page)
            self.assertNotIn('data-isloaded="false"', page)
            self.assertEqual(page.count("<script"), 1)
            self.assertIn("/geisha/zshop-bridge.js", page)
            self.assertNotIn("js/minified/boot.js", page)
            self.assertIn("Demo &lt;script&gt;x&lt;/script&gt;", page)
            self.assertLess(page.index("Demo &lt;script&gt;"), page.index("Second demo"))
            self.assertEqual((geisha / "index.html").read_text(encoding="utf-8"),
                             ARCHIVED_HOME)

    def test_missing_catalog_still_exits_loading_state(self):
        page = hydrate_index(ARCHIVED_HOME, [])
        self.assertIn("No local demo catalog", page)
        self.assertNotIn("Loading...", page)

    def test_unknown_layout_not_modified(self):
        other = '<div id="other">Loading...</div>'
        self.assertEqual(hydrate_index(other, []), other)

    def test_non_index_page_does_not_get_home_menu_injected(self):
        with tempfile.TemporaryDirectory() as temp:
            geisha = Path(temp) / "geisha"
            geisha.mkdir()
            (geisha / "index.html").write_text(ARCHIVED_HOME, encoding="utf-8")
            (geisha / "shelf02_01.html").write_text(
                '<html><body><h1>Charts</h1></body></html>', encoding="utf-8")
            archive = GeishaArchive(temp, [{"name": "a", "popularity": 1}])
            _, html = archive.read("/geisha/shelf02_01.html")
            self.assertNotIn(b"ft_navi", html)
            self.assertNotIn(b"zshop-geisha-visibility", html)
            self.assertIn(b"Charts", html)

    def test_no_account_or_download_actions(self):
        page = hydrate_index(ARCHIVED_HOME, [{"name": "Demo", "popularity": 1}])
        for forbidden in (
            "registerTitleDownloadTask", "ticketDownloadSync",
            "ninja/ws/my", "href=\"money01_01.html\"",
            "href=\"always01_01.html\"", "onclick=",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, page)

    def test_secondary_wrapper_revealed_without_home_hydration(self):
        from geisha_archive import preview_html
        html = b'<html><head></head><body><div id="wrapper">Charts</div></body></html>'
        page = preview_html(html, 'shelf02_01.html').decode()
        self.assertIn('#wrapper{display:block!important}', page)
        self.assertNotIn('top-content', page)


if __name__ == "__main__":
    unittest.main()
