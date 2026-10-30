"""Real rendering regression; synthetic fixture, no Nintendo resources."""
import base64
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@unittest.skipUnless(os.environ.get('ZSHOP_BROWSER_ENGINE'),
                     'Set ZSHOP_BROWSER_ENGINE=chromium or webkit for browser checks')
class BrowserRegressionTests(unittest.TestCase):
    def test_http_dom_assets_and_native_failure_matrix(self):
        from tools.check_geisha_browser import check_archive
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'source'
            root.mkdir()
            (root / 'css').mkdir()
            (root / 'image/placeholder').mkdir(parents=True)
            (root / 'index.html').write_text(
                '<!doctype html><html><head><meta charset="utf-8">'
                '<link rel="stylesheet" href="css/test.css"></head><body>'
                '<div id="wrapper"><ul id="el-top"><li>Loading...</li></ul>'
                '<div id="sel_menu_bar"></div></div>'
                '<script>throw Error("archive JS must never execute");</script>'
                '</body></html>', encoding='utf-8')
            (root / 'css/test.css').write_text(
                '#wrapper{display:none;width:1280px;min-height:720px}'
                'body{margin:0;background:#eee}#el-top{margin-left:180px}', encoding='utf-8')
            (root / 'shelf02_01.html').write_text(
                '<html><head><link rel="stylesheet" href="css/test.css"></head>'
                '<body><div id="wrapper">Synthetic secondary page</div></body></html>', encoding='utf-8')
            pixel = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1Pe'
                                     'AAAADElEQVR4nGP4//8/AAX+Av4N70a4AAAAAElFTkSuQmCC')
            (root / 'image/placeholder/place_banner.png').write_bytes(pixel)
            (root / 'image/img_unknown_MiiIcon.png').write_bytes(pixel)
            report = check_archive(root, Path(directory) / 'renders',
                                   os.environ['ZSHOP_BROWSER_ENGINE'],
                                   os.environ.get('ZSHOP_BROWSER_CHANNEL'))
            for case in report['cases']:
                with self.subTest(case=case['name']):
                    self.assertTrue(case['passed'], case.get('reason'))


    def test_archived_search_flow_renders_in_browser(self):
        """A real form click must load the historical shelf with its own wrapper."""
        from http.server import ThreadingHTTPServer
        from threading import Thread
        from playwright.sync_api import sync_playwright
        from backend import make_handler
        from geisha_archive import GeishaArchive

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'geisha'
            (root / 'css').mkdir(parents=True)
            (root / 'image/placeholder').mkdir(parents=True)
            (root / 'index.html').write_text(
                '<html><head></head><body><div id="wrapper">Home</div></body></html>',
                encoding='utf-8')
            (root / 'always02_01.html').write_text(
                '<html><head><link rel="stylesheet" href="css/test.css"></head>'
                '<body><div id="wrapper"><div id="header">'
                '<input name="freeword" class="textbox">'
                '<a href="#" class="search-submit se"><span class="search-label">'
                'Search</span></a></div></div></body></html>', encoding='utf-8')
            (root / 'shelf02_01.html').write_text(
                '<html><head><link rel="stylesheet" href="css/test.css"></head>'
                '<body><div id="wrapper" class="js-top">Boot</div>'
                '<div id="wrapper" class="js-shelf"><h1>Charts</h1>'
                '<span class="total-results">Results: 83</span>'
                '<ul id="shelf-list" class="shelf-list-item" data-isloaded="false">'
                '<p class="loading">Loading...</p></ul></div></body></html>',
                encoding='utf-8')
            (root / 'css/test.css').write_text(
                '#wrapper{display:none;width:1280px;min-height:720px}',
                encoding='utf-8')
            archive = GeishaArchive(root, [
                {'name': 'Corsa Zero', 'category': 'race',
                 'description': 'demo', 'popularity': 10, 'release': '2026-10-01'},
                {'name': 'Puzzle Aurora', 'category': 'puzzle',
                 'description': 'demo', 'popularity': 5, 'release': '2026-10-04'},
            ])
            server = ThreadingHTTPServer(
                ('127.0.0.1', 0), make_handler([], geisha=archive)
            )
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = 'http://127.0.0.1:%s' % server.server_address[1]
            try:
                with sync_playwright() as playwright:
                    browser_type = getattr(
                        playwright, os.environ['ZSHOP_BROWSER_ENGINE'])
                    browser = browser_type.launch(headless=True)
                    try:
                        page = browser.new_page(viewport={'width': 1280, 'height': 720})
                        page.goto(base + '/geisha/always02_01.html',
                                  wait_until='load')
                        self.assertTrue(page.locator('form#zshop-safe-search').is_visible())
                        page.locator('input[name="freeword"]').fill('Corsa')
                        page.locator('button.search-submit').click()
                        page.wait_for_url('**/geisha/shelf02_01.html?freeword=Corsa')
                        self.assertEqual(page.locator('li.m-list-item').count(), 1)
                        self.assertIn('Corsa Zero', page.locator('#shelf-list').inner_text())
                        self.assertNotIn('Puzzle Aurora', page.locator('#shelf-list').inner_text())
                        self.assertEqual(
                            page.locator('#wrapper.js-shelf').evaluate(
                                'el => getComputedStyle(el).display'), 'block')
                        self.assertEqual(
                            page.locator('#wrapper.js-top').evaluate(
                                'el => getComputedStyle(el).display'), 'none')
                    finally:
                        browser.close()
            finally:
                server.shutdown()
                thread.join(timeout=3)
                server.server_close()


if __name__ == '__main__':
    unittest.main()
