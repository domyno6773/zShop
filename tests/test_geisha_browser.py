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
            pixel = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwC'
                                     'AAAAC0lEQVR42mP8/x8AAwMCAO+a6QAAAABJRU5ErkJggg==')
            (root / 'image/placeholder/place_banner.png').write_bytes(pixel)
            (root / 'image/img_unknown_MiiIcon.png').write_bytes(pixel)
            report = check_archive(root, Path(directory) / 'renders',
                                   os.environ['ZSHOP_BROWSER_ENGINE'],
                                   os.environ.get('ZSHOP_BROWSER_CHANNEL'))
            for case in report['cases']:
                with self.subTest(case=case['name']):
                    self.assertTrue(case['passed'], case.get('reason'))


if __name__ == '__main__':
    unittest.main()
